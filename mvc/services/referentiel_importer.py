# pyright: strict
"""Importeur d'un référentiel niveau-classe depuis son JSON canonique (ticket 11).

Logique pure : prend un canonique **déjà validé** (dict) et le persiste via
`core.database.db` (SQL visible et paramétré, esprit Forge). Indépendant de l'UI admin.

Décisions (ADR-011) :
- **Upsert par identifiant** : ré-importer un même `identifiant` remplace le contenu du
  référentiel (purge des objets rattachés puis ré-insertion).
- **Best-effort avec rapport** : chaque élément est inséré isolément ; un échec est
  journalisé dans le rapport et n'interrompt pas l'import.

Les identifiants/codes locaux du canonique (`pole.id`, `activite.code`, `competence.code`,
`famille.code`) sont mappés vers les `Id` de la base au fil des insertions, pour résoudre
les FK et les liens many_to_many (`activite_competence`, `cc_competence`).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, cast

from core.database import db


def _empty_counts() -> dict[str, int]:
    return {}


def _empty_errors() -> list[str]:
    return []


@dataclass
class ImportReport:
    """Compte-rendu best-effort d'un import (ADR-011)."""

    identifiant: str = ""
    referentiel_id: int | None = None
    remplacement: bool = False
    inseres: dict[str, int] = field(default_factory=_empty_counts)
    erreurs: list[str] = field(default_factory=_empty_errors)

    def compte(self, categorie: str) -> None:
        self.inseres[categorie] = self.inseres.get(categorie, 0) + 1

    def echec(self, contexte: str, exc: Exception) -> None:
        self.erreurs.append(f"{contexte} : {exc}")

    @property
    def ok(self) -> bool:
        return not self.erreurs


def _as_int(value: Any) -> int:
    return int(cast("int", value))


# Un nom de table ne peut pas être un paramètre SQL (`?`) : il est interpolé en
# f-string. Cette liste blanche garantit que seuls des littéraux connus du module
# atteignent l'interpolation, même si un appelant futur passait une valeur externe.
_TABLES_UPSERT = frozenset({"formation", "niveau_classe"})


def _upsert_par_code(table: str, code: str, intitule: str, type_: "str | None" = None) -> int:
    """Insère ou met à jour une entité identifiée par sa colonne `Code` unique.

    `type_` alimente la colonne `Type` (formation, ADR-023) quand elle existe ;
    laissé à None pour les tables sans cette colonne (ex. niveau_classe).
    """
    if table not in _TABLES_UPSERT:
        raise ValueError(f"table non autorisée pour l'upsert : {table!r}")
    existant = db.fetch_one(f"SELECT Id FROM {table} WHERE Code = ?", (code,))
    if existant is not None:
        if type_ is not None:
            db.execute(
                f"UPDATE {table} SET Type = ?, Intitule = ?, UpdatedAt = NOW() WHERE Id = ?",
                (type_, intitule, existant["Id"]),
            )
        else:
            db.execute(
                f"UPDATE {table} SET Intitule = ?, UpdatedAt = NOW() WHERE Id = ?",
                (intitule, existant["Id"]),
            )
        return _as_int(existant["Id"])
    if type_ is not None:
        return db.insert(
            f"INSERT INTO {table} (Code, Type, Intitule, CreatedAt, UpdatedAt) VALUES (?, ?, ?, NOW(), NOW())",
            (code, type_, intitule),
        )
    return db.insert(
        f"INSERT INTO {table} (Code, Intitule, CreatedAt, UpdatedAt) VALUES (?, ?, NOW(), NOW())",
        (code, intitule),
    )


def _upsert_referentiel(canonical: dict[str, Any], formation_id: int) -> tuple[int, bool]:
    """Insère ou met à jour le référentiel (clé = `Identifiant`). Retourne (id, remplacement).

    Le référentiel appartient à une formation (ADR-023), plus à un niveau de classe.
    """
    identifiant = str(canonical["identifiant"])
    version = str(canonical.get("version", ""))
    statut = str(canonical.get("statut", "brouillon"))
    existant = db.fetch_one(
        "SELECT Id FROM referentiel_niveau_classe WHERE Identifiant = ?", (identifiant,)
    )
    if existant is not None:
        ref_id = _as_int(existant["Id"])
        db.execute(
            "UPDATE referentiel_niveau_classe "
            "SET Version = ?, Statut = ?, ImporteLe = NOW(), formation_id = ?, "
            "UpdatedAt = NOW() WHERE Id = ?",
            (version, statut, formation_id, ref_id),
        )
        return ref_id, True
    ref_id = db.insert(
        "INSERT INTO referentiel_niveau_classe "
        "(Identifiant, Version, Statut, ImporteLe, formation_id, CreatedAt, UpdatedAt) "
        "VALUES (?, ?, ?, NOW(), ?, NOW(), NOW())",
        (identifiant, version, statut, formation_id),
    )
    return ref_id, False


def _purge_contenu(ref_id: int) -> None:
    """Supprime tout le contenu rattaché à un référentiel, dans l'ordre des dépendances
    (enfants avant parents, FK RESTRICT). Utilisé avant ré-insertion (upsert)."""
    r = (ref_id,)
    # Pivots m2m d'abord.
    db.execute(
        "DELETE FROM activite_competence WHERE activite_professionnelle_id IN "
        "(SELECT Id FROM activite_professionnelle WHERE referentiel_id = ?)",
        r,
    )
    db.execute(
        "DELETE FROM cc_competence WHERE famille_competence_id IN "
        "(SELECT Id FROM famille_competence WHERE referentiel_id = ?)",
        r,
    )
    # Petits-enfants (via activité / compétence).
    db.execute(
        "DELETE FROM tache WHERE activite_id IN "
        "(SELECT Id FROM activite_professionnelle WHERE referentiel_id = ?)",
        r,
    )
    db.execute(
        "DELETE FROM resultat_attendu WHERE activite_id IN "
        "(SELECT Id FROM activite_professionnelle WHERE referentiel_id = ?)",
        r,
    )
    db.execute(
        "DELETE FROM critere_observable WHERE competence_id IN "
        "(SELECT Id FROM competence WHERE referentiel_id = ?)",
        r,
    )
    db.execute(
        "DELETE FROM connaissance WHERE competence_id IN "
        "(SELECT Id FROM competence WHERE referentiel_id = ?)",
        r,
    )
    # Enfants directs. (indicateur_reussite est rattaché au CRITERE depuis ADR-022 —
    # pas de colonne referentiel_id ; il est déjà purgé en CASCADE avec les critères.)
    for table in (
        "source", "activite_professionnelle",
        "competence", "pole_activite", "famille_competence",
    ):
        db.execute(f"DELETE FROM {table} WHERE referentiel_id = ?", r)


def _importer_sources(canonical: dict[str, Any], ref_id: int, rapport: ImportReport) -> None:
    for src in canonical.get("sources", []):
        try:
            db.insert(
                "INSERT INTO source (SourceId, SourceType, SourceFichier, SourceNote, "
                "referentiel_id, CreatedAt, UpdatedAt) VALUES (?, ?, ?, ?, ?, NOW(), NOW())",
                (src.get("source_id", ""), src.get("source_type", ""),
                 src.get("source_fichier", ""), src.get("source_note"), ref_id),
            )
            rapport.compte("sources")
        except Exception as exc:  # noqa: BLE001 (best-effort, ADR-011)
            rapport.echec(f"source {src.get('source_id')}", exc)


def import_referentiel(canonical: dict[str, Any]) -> ImportReport:
    """Importe un canonique validé en base. Retourne un rapport best-effort (ADR-011)."""
    rapport = ImportReport(identifiant=str(canonical.get("identifiant", "")))

    # ADR-023 : le référentiel appartient à une formation (le niveau de classe n'en
    # est plus une propriété). On importe formation ET niveau_classe (tous deux au
    # contrat, cf. schema-json-canonique-referentiel-niveau-classe.json), upsert par
    # Code. Le PONT `formation_niveau` (formation × niveau, avec ordre) n'est PAS
    # porté par le canonique : il reste une donnée d'établissement, construit hors
    # import (phase 1d, cf. mvc/fixtures/structure.py).
    formation = canonical["formation"]
    formation_id = _upsert_par_code(
        "formation", str(formation["code"]), str(formation["intitule"]),
        type_=str(formation.get("type", "AUTRE")),
    )
    niveau = canonical.get("niveau_classe")
    if niveau is not None:
        _upsert_par_code("niveau_classe", str(niveau["code"]), str(niveau["intitule"]))

    ref_id, remplacement = _upsert_referentiel(canonical, formation_id)
    rapport.referentiel_id = ref_id
    rapport.remplacement = remplacement
    if remplacement:
        _purge_contenu(ref_id)

    _importer_sources(canonical, ref_id, rapport)

    # Pôles : id local -> Id base.
    pole_map: dict[str, int] = {}
    for pole in canonical.get("poles_activites", []):
        try:
            pid = db.insert(
                "INSERT INTO pole_activite (Intitule, referentiel_id, CreatedAt, UpdatedAt) "
                "VALUES (?, ?, NOW(), NOW())",
                (pole["intitule"], ref_id),
            )
            pole_map[str(pole["id"])] = pid
            rapport.compte("poles")
        except Exception as exc:  # noqa: BLE001
            rapport.echec(f"pole {pole.get('id')}", exc)

    # Compétences : code -> Id base (+ critères imbriqués).
    comp_map: dict[str, int] = {}
    crit_map: dict[str, int] = {}  # id canonique du critère (ex. cr-c06-1) -> Id base
    for comp in canonical.get("competences", []):
        try:
            cid = db.insert(
                "INSERT INTO competence (Code, Intitule, referentiel_id, CreatedAt, UpdatedAt) "
                "VALUES (?, ?, ?, NOW(), NOW())",
                (comp["code"], comp["intitule"], ref_id),
            )
            comp_map[str(comp["code"])] = cid
            rapport.compte("competences")
            for conn in comp.get("connaissances", []):
                try:
                    db.insert(
                        "INSERT INTO connaissance (Libelle, NiveauTaxonomique, competence_id, "
                        "CreatedAt, UpdatedAt) VALUES (?, ?, ?, NOW(), NOW())",
                        (conn["libelle"], conn.get("niveau_taxonomique"), cid),
                    )
                    rapport.compte("connaissances")
                except Exception as exc:  # noqa: BLE001
                    rapport.echec(f"connaissance {conn.get('libelle')}", exc)
            for crit in comp.get("criteres_evaluation", []):
                try:
                    crit_id = db.insert(
                        "INSERT INTO critere_observable (Code, Libelle, SavoirEtre, competence_id, "
                        "CreatedAt, UpdatedAt) VALUES (?, ?, ?, ?, NOW(), NOW())",
                        (crit["id"], crit["libelle"], 1 if crit.get("savoir_etre") else 0, cid),
                    )
                    crit_map[str(crit["id"])] = crit_id
                    rapport.compte("criteres")
                except Exception as exc:  # noqa: BLE001
                    rapport.echec(f"critere {crit.get('id')}", exc)
        except Exception as exc:  # noqa: BLE001
            rapport.echec(f"competence {comp.get('code')}", exc)

    # Activités : code -> Id base (+ tâches et résultats imbriqués).
    act_map: dict[str, int] = {}
    for act in canonical.get("activites_professionnelles", []):
        try:
            pole_id = pole_map.get(str(act.get("pole_id")))
            if pole_id is None:
                rapport.echec(f"activite {act.get('code')}", ValueError(f"pole_id orphelin {act.get('pole_id')}"))
                continue
            aid = db.insert(
                "INSERT INTO activite_professionnelle (Code, Intitule, ConditionsExercice, "
                "referentiel_id, pole_id, CreatedAt, UpdatedAt) VALUES (?, ?, ?, ?, ?, NOW(), NOW())",
                (act["code"], act["intitule"], act.get("conditions_exercice"), ref_id, pole_id),
            )
            act_map[str(act["code"])] = aid
            rapport.compte("activites")
            for i, tache in enumerate(act.get("taches", []), start=1):
                try:
                    db.insert(
                        "INSERT INTO tache (Ordre, Libelle, activite_id, CreatedAt, UpdatedAt) "
                        "VALUES (?, ?, ?, NOW(), NOW())",
                        (i, tache, aid),
                    )
                    rapport.compte("taches")
                except Exception as exc:  # noqa: BLE001
                    rapport.echec(f"tache {i} de {act.get('code')}", exc)
            for res in act.get("resultats_attendus", []):
                try:
                    db.insert(
                        "INSERT INTO resultat_attendu (Code, Libelle, activite_id, CreatedAt, UpdatedAt) "
                        "VALUES (?, ?, ?, NOW(), NOW())",
                        (res["id"], res["libelle"], aid),
                    )
                    rapport.compte("resultats")
                except Exception as exc:  # noqa: BLE001
                    rapport.echec(f"resultat {res.get('id')}", exc)
        except Exception as exc:  # noqa: BLE001
            rapport.echec(f"activite {act.get('code')}", exc)

    # Familles de compétences : code -> Id base.
    famille_map: dict[str, int] = {}
    for fam in canonical.get("famille_competences", []):
        try:
            fid = db.insert(
                "INSERT INTO famille_competence (Code, Intitule, referentiel_id, CreatedAt, UpdatedAt) "
                "VALUES (?, ?, ?, NOW(), NOW())",
                (fam["code"], fam["intitule"], ref_id),
            )
            famille_map[str(fam["code"])] = fid
            rapport.compte("familles")
        except Exception as exc:  # noqa: BLE001
            rapport.echec(f"famille {fam.get('code')}", exc)

    # Indicateurs de réussite (ADR-022, option A) : un indicateur n'existe QUE
    # rattaché à un critère. Les amorces d'autre origine (résultat attendu,
    # reformulation) ne sont pas importées ; le professeur les recrée sur un critère.
    for ind in canonical.get("indicateurs_reussite", []):
        if ind.get("origine") != "critere":
            continue
        crit_id = crit_map.get(str(ind.get("ref")))
        if crit_id is None:
            rapport.echec(f"indicateur {ind.get('id')}", ValueError(f"critère orphelin {ind.get('ref')}"))
            continue
        try:
            db.insert(
                "INSERT INTO indicateur_reussite (Code, Libelle, critere_id, CreatedAt, UpdatedAt) "
                "VALUES (?, ?, ?, NOW(), NOW())",
                (ind["id"], ind["libelle"], crit_id),
            )
            rapport.compte("indicateurs")
        except Exception as exc:  # noqa: BLE001
            rapport.echec(f"indicateur {ind.get('id')}", exc)

    _importer_liens(canonical, act_map, comp_map, famille_map, rapport)
    return rapport


def _importer_liens(
    canonical: dict[str, Any],
    act_map: dict[str, int],
    comp_map: dict[str, int],
    famille_map: dict[str, int],
    rapport: ImportReport,
) -> None:
    """Liens many_to_many : activité↔compétence (pivot) et famille↔compétence (pivot)."""
    relations = canonical.get("relations", {})
    for lien in relations.get("activites_competences", []):
        aid = act_map.get(str(lien.get("activite")))
        if aid is None:
            rapport.echec("lien activite_competence", ValueError(f"activite orpheline {lien.get('activite')}"))
            continue
        for code_comp in lien.get("competences", []):
            cid = comp_map.get(str(code_comp))
            if cid is None:
                rapport.echec("lien activite_competence", ValueError(f"competence orpheline {code_comp}"))
                continue
            try:
                db.insert(
                    "INSERT INTO activite_competence (activite_professionnelle_id, competence_id) "
                    "VALUES (?, ?)",
                    (aid, cid),
                )
                rapport.compte("activite_competence")
            except Exception as exc:  # noqa: BLE001
                rapport.echec(f"activite_competence {lien.get('activite')}/{code_comp}", exc)

    for lien in relations.get("cc_competences", []):
        fid = famille_map.get(str(lien.get("cc")))
        if fid is None:
            rapport.echec("lien cc_competence", ValueError(f"famille orpheline {lien.get('cc')}"))
            continue
        for code_comp in lien.get("competences", []):
            cid = comp_map.get(str(code_comp))
            if cid is None:
                rapport.echec("lien cc_competence", ValueError(f"competence orpheline {code_comp}"))
                continue
            try:
                db.insert(
                    "INSERT INTO cc_competence (famille_competence_id, competence_id) VALUES (?, ?)",
                    (fid, cid),
                )
                rapport.compte("cc_competence")
            except Exception as exc:  # noqa: BLE001
                rapport.echec(f"cc_competence {lien.get('cc')}/{code_comp}", exc)
