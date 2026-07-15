# pyright: strict
"""Modèle de lecture de l'atelier référentiel (ADR-018).

Assemble l'arbre complet d'un référentiel niveau-classe pour une vue cohérente
(consultation), à partir des mêmes tables que `referentiel_importer`. SQL visible
et paramétré (esprit Forge) ; jointures plutôt que des `IN (...)` dynamiques.

Structure de l'arbre retourné par `get_arbre` :
    sources[], indicateurs[],
    poles[{ ..., activites[{ ..., taches[], resultats[] }] }],
    competences[{ ..., criteres[] }],
    familles[{ ..., competences[] }]  (lien many_to_many cc_competence)
"""
from typing import Any

from core.database.db import execute, fetch_all, fetch_one, insert


def list_referentiels() -> list[dict[str, Any]]:
    """Tous les référentiels, avec le libellé de formation et le niveau."""
    return fetch_all(
        "SELECT r.Id, r.Identifiant, r.Version, r.Statut, r.ImporteLe, "
        "f.Intitule AS formation_intitule, "
        "nc.Code AS niveau_code, nc.Intitule AS niveau_intitule "
        "FROM referentiel_niveau_classe r "
        "LEFT JOIN formation f ON f.Id = r.formation_id "
        "LEFT JOIN niveau_classe nc ON nc.Id = r.niveau_classe_id "
        "ORDER BY r.Identifiant"
    )


def get_referentiel(ref_id: int) -> "dict[str, Any] | None":
    """L'en-tête d'un référentiel (identité, version, statut, formation, niveau)."""
    return fetch_one(
        "SELECT r.Id, r.Identifiant, r.Version, r.Statut, r.ImporteLe, "
        "f.Code AS formation_code, f.Intitule AS formation_intitule, "
        "nc.Code AS niveau_code, nc.Intitule AS niveau_intitule "
        "FROM referentiel_niveau_classe r "
        "LEFT JOIN formation f ON f.Id = r.formation_id "
        "LEFT JOIN niveau_classe nc ON nc.Id = r.niveau_classe_id "
        "WHERE r.Id = ?",
        (ref_id,),
    )


def _group_by(rows: list[dict[str, Any]], key: str) -> dict[Any, list[dict[str, Any]]]:
    """Regroupe des lignes par la valeur d'une colonne clé."""
    out: dict[Any, list[dict[str, Any]]] = {}
    for row in rows:
        out.setdefault(row[key], []).append(row)
    return out


def get_arbre(ref_id: int) -> dict[str, Any]:
    """Assemble l'arbre complet d'un référentiel pour l'affichage maître-détail."""
    r = (ref_id,)

    sources = fetch_all(
        "SELECT Id, SourceId, SourceType, SourceFichier, SourceNote "
        "FROM source WHERE referentiel_id = ? ORDER BY SourceId",
        r,
    )
    # Indicateurs de réussite : rattachés à un CRITERE (ADR-022, option A). On les
    # charge via le critère (le référentiel se déduit de critère -> compétence).
    indicateurs = fetch_all(
        "SELECT ind.Id, ind.Code, ind.Libelle, ind.critere_id "
        "FROM indicateur_reussite ind "
        "JOIN critere_observable c ON c.Id = ind.critere_id "
        "JOIN competence cp ON cp.Id = c.competence_id "
        "WHERE cp.referentiel_id = ? ORDER BY ind.Code",
        r,
    )

    # Pôles -> activités -> (tâches, résultats).
    poles = fetch_all(
        "SELECT Id, Intitule FROM pole_activite WHERE referentiel_id = ? ORDER BY Id", r
    )
    activites = fetch_all(
        "SELECT Id, Code, Intitule, ConditionsExercice, pole_id "
        "FROM activite_professionnelle WHERE referentiel_id = ? ORDER BY pole_id, Code",
        r,
    )
    taches = fetch_all(
        "SELECT t.Id, t.Ordre, t.Libelle, t.activite_id "
        "FROM tache t JOIN activite_professionnelle a ON a.Id = t.activite_id "
        "WHERE a.referentiel_id = ? ORDER BY t.activite_id, t.Ordre",
        r,
    )
    resultats = fetch_all(
        "SELECT ra.Id, ra.Code, ra.Libelle, ra.activite_id "
        "FROM resultat_attendu ra JOIN activite_professionnelle a ON a.Id = ra.activite_id "
        "WHERE a.referentiel_id = ? ORDER BY ra.activite_id, ra.Code",
        r,
    )
    taches_par_act = _group_by(taches, "activite_id")
    resultats_par_act = _group_by(resultats, "activite_id")
    act_par_pole = _group_by(activites, "pole_id")
    for act in activites:
        act["taches"] = taches_par_act.get(act["Id"], [])
        act["resultats"] = resultats_par_act.get(act["Id"], [])
    for pole in poles:
        pole["activites"] = act_par_pole.get(pole["Id"], [])

    # Compétences -> critères observables.
    competences = fetch_all(
        "SELECT Id, Code, Intitule FROM competence WHERE referentiel_id = ? ORDER BY Code", r
    )
    criteres = fetch_all(
        "SELECT c.Id, c.Code, c.Libelle, c.competence_id "
        "FROM critere_observable c JOIN competence cp ON cp.Id = c.competence_id "
        "WHERE cp.referentiel_id = ? ORDER BY c.competence_id, c.Code",
        r,
    )
    # Indicateurs nichés sous leur critère (Critère 1 - 0..n Indicateur).
    ind_par_crit = _group_by(indicateurs, "critere_id")
    for crit in criteres:
        crit["indicateurs"] = ind_par_crit.get(crit["Id"], [])
    criteres_par_comp = _group_by(criteres, "competence_id")
    for comp in competences:
        comp["criteres"] = criteres_par_comp.get(comp["Id"], [])

    # Familles -> compétences (lien many_to_many cc_competence).
    familles = fetch_all(
        "SELECT Id, Code, Intitule FROM famille_competence WHERE referentiel_id = ? ORDER BY Code", r
    )
    liens_fc = fetch_all(
        "SELECT cc.famille_competence_id, cp.Id, cp.Code, cp.Intitule "
        "FROM cc_competence cc JOIN competence cp ON cp.Id = cc.competence_id "
        "JOIN famille_competence f ON f.Id = cc.famille_competence_id "
        "WHERE f.referentiel_id = ? ORDER BY cp.Code",
        r,
    )
    comp_par_famille = _group_by(liens_fc, "famille_competence_id")
    for fam in familles:
        fam["competences"] = comp_par_famille.get(fam["Id"], [])

    return {
        "sources": sources,
        "indicateurs": indicateurs,
        "poles": poles,
        "competences": competences,
        "familles": familles,
    }


def get_critere(critere_id: int) -> "dict[str, Any] | None":
    """Un critère (pour valider son existence avant d'y attacher un indicateur)."""
    return fetch_one(
        "SELECT Id, Code, Libelle, competence_id FROM critere_observable WHERE Id = ?",
        (critere_id,),
    )


def ajouter_indicateur(critere_id: int, libelle: str) -> int:
    """Ajoute un indicateur de réussite à un critère (code local auto-généré)."""
    row = fetch_one("SELECT COUNT(*) AS n FROM indicateur_reussite WHERE critere_id = ?", (critere_id,))
    n = int(row["n"]) if row else 0
    code = f"ind-c{critere_id}-{n + 1}"
    return insert(
        "INSERT INTO indicateur_reussite (Code, Libelle, critere_id, CreatedAt, UpdatedAt) "
        "VALUES (?, ?, ?, NOW(), NOW())",
        (code, libelle, critere_id),
    )


def supprimer_indicateur(indicateur_id: int) -> None:
    """Supprime un indicateur de réussite."""
    execute("DELETE FROM indicateur_reussite WHERE Id = ?", (indicateur_id,))
