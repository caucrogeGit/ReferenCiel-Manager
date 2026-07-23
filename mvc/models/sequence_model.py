from datetime import datetime, timezone

from typing import Any

from core.database.db import fetch_one, fetch_all, execute, insert
from mvc.services.sequence_tunnel import mode_organisation, statut_sequence_cible, statuts_ouvrants_pour_nature

# Liste des cartes : classée par référentiel (via le scénario appairé, 1-1),
# hors référentiel en fin, puis par titre.
SELECT_ALL   = (
    "SELECT sequence.*, niveau_classe.Code AS niveau_classe_id_label, "
    "r.Identifiant AS referentiel_identifiant, f.Intitule AS formation_intitule "
    "FROM sequence "
    "LEFT JOIN niveau_classe ON sequence.niveau_classe_id = niveau_classe.Id "
    "LEFT JOIN scenario_sequence ss ON ss.sequence_id = sequence.Id "
    "LEFT JOIN scenario sc ON sc.Id = ss.scenario_id "
    "LEFT JOIN referentiel_niveau_classe r ON r.Id = sc.referentiel_id "
    "LEFT JOIN formation f ON f.Id = r.formation_id "
    "ORDER BY (r.Identifiant IS NULL), r.Identifiant, sequence.Titre, sequence.Id"
)
SELECT_BY_ID = "SELECT sequence.*, niveau_classe.Code AS niveau_classe_id_label FROM sequence LEFT JOIN niveau_classe ON sequence.niveau_classe_id = niveau_classe.Id WHERE sequence.Id = ?"
INSERT       = "INSERT INTO sequence (Identifiant, Titre, Presentation, Statut, ActiviteGlissante, OrdreImpose, Prerequis, PositionnementProgression, DureeEstimee, ModalitesEvaluation, niveau_classe_id, CreatedAt, UpdatedAt) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
UPDATE       = "UPDATE sequence SET Identifiant = ?, Titre = ?, Presentation = ?, Statut = ?, ActiviteGlissante = ?, OrdreImpose = ?, Prerequis = ?, PositionnementProgression = ?, DureeEstimee = ?, ModalitesEvaluation = ?, niveau_classe_id = ?, UpdatedAt = ? WHERE Id = ?"
DELETE       = "DELETE FROM sequence WHERE Id = ?"


def get_sequences():
    return fetch_all(SELECT_ALL)


def get_sequence_by_id(id):
    return fetch_one(SELECT_BY_ID, (id,))


def add_sequence(data):
    return insert(INSERT, (data["identifiant"], data["titre"], data["presentation"], data["statut"], data["activite_glissante"], data["ordre_impose"], data["prerequis"], data["positionnement_progression"], data["duree_estimee"], data["modalites_evaluation"], data["niveau_classe_id"], datetime.now(timezone.utc), datetime.now(timezone.utc),))


def update_sequence(id, data):
    execute(UPDATE, (data["identifiant"], data["titre"], data["presentation"], data["statut"], data["activite_glissante"], data["ordre_impose"], data["prerequis"], data["positionnement_progression"], data["duree_estimee"], data["modalites_evaluation"], data["niveau_classe_id"], datetime.now(timezone.utc), id))


UPDATE_IDENTITE = "UPDATE sequence SET Titre = ?, ActiviteGlissante = ?, OrdreImpose = ?, Nature = ?, niveau_classe_id = ?, UpdatedAt = ? WHERE Id = ?"


def recalculer_statut(sequence_id: int) -> None:
    """Recalcule et persiste le statut de la séquence (ADR-034, miroir du scénario).

    Cycle ENTIÈREMENT dérivé des données : brouillon (tunnel incomplet),
    finalise (complet), publie (complet + au moins une séance liée), attribue
    (au moins une progression élève, qui prime sur tout).
    """
    seq = fetch_one(
        "SELECT Titre, niveau_classe_id, Statut, Nature, ActiviteGlissante, OrdreImpose "
        "FROM sequence WHERE Id = ?", (sequence_id,))
    if seq is None:
        return
    ref = fetch_one(
        "SELECT s.referentiel_id AS ref FROM scenario_sequence ss "
        "JOIN scenario s ON s.Id = ss.scenario_id WHERE ss.sequence_id = ? LIMIT 1",
        (sequence_id,),
    )
    # ADR-037 : les savoirs vivent sur la SÉANCE. La publication exige au moins
    # une séance OUVRANTE (≥ 1 savoir validé au statut ouvrant pour la nature).
    ouvrants = statuts_ouvrants_pour_nature(seq.get("Nature"))
    marqueurs = ", ".join("?" for _ in ouvrants)
    nb_ouvrantes = fetch_one(
        "SELECT COUNT(DISTINCT sk.seance_id) AS n FROM seance_connaissance sk "
        "JOIN seance se ON se.Id = sk.seance_id "
        "WHERE se.sequence_id = ? AND sk.NiveauCible IS NOT NULL AND sk.Statut IN (" + marqueurs + ")",
        (sequence_id, *ouvrants),
    )
    nb_seances = fetch_one(
        "SELECT COUNT(*) AS n FROM seance WHERE sequence_id = ?",
        (sequence_id,),
    )
    nb_attributions = fetch_one(
        "SELECT COUNT(*) AS n FROM progression_sequence WHERE sequence_id = ?",
        (sequence_id,),
    )
    statut = statut_sequence_cible(
        seq["Titre"],
        seq["niveau_classe_id"],
        ref["ref"] if ref else None,
        int(nb_seances["n"]) if nb_seances else 0,
        int(nb_ouvrantes["n"]) if nb_ouvrantes else 0,
        int(nb_attributions["n"]) if nb_attributions else 0,
        mode_organisation(seq),
    )
    if statut != seq["Statut"]:
        execute(
            "UPDATE sequence SET Statut = ?, UpdatedAt = ? WHERE Id = ?",
            (statut, datetime.now(timezone.utc), sequence_id),
        )


# DureeEstimee et Prerequis ne sont plus écrits ici : ces deux valeurs sont
# DÉRIVÉES des séances rattachées (seance_model.duree_cumulee_minutes et
# prerequis_par_seance). Les colonnes subsistent au contrat pour l'historique
# et le CRUD générique.
UPDATE_CADRE    = "UPDATE sequence SET PositionnementProgression = ?, ModalitesEvaluation = ?, UpdatedAt = ? WHERE Id = ?"


def update_identite(id, data):
    """Auto-save de l'étape Titre du tunnel. L'Identifiant (technique, dérivé du
    titre à la création) n'est pas géré par le professeur : on n'y touche pas."""
    execute(UPDATE_IDENTITE, (data["titre"], data["activite_glissante"], data["ordre_impose"], data["nature"], data["niveau_classe_id"], datetime.now(timezone.utc), id))


def update_cadre(id, data):
    """Auto-save de l'étape Cadre institutionnel (colonnes SEQ-02 seulement)."""
    execute(UPDATE_CADRE, (data["positionnement_progression"], data["modalites_evaluation"], datetime.now(timezone.utc), id))


def delete_sequence(id):
    execute(DELETE, (id,))


def motif_blocage_suppression(sequence_id):
    """Raison humaine empêchant la suppression (FK restrict au contrat), ou None.

    Les séances liées et les progressions d'élèves bloquent ; les savoirs
    (connaissances, savoirs libres) partent en CASCADE.
    """
    row = fetch_one(
        "SELECT COUNT(*) AS n FROM progression_sequence WHERE sequence_id = ?",
        (sequence_id,),
    )
    if row and int(row["n"]) > 0:
        return "des progressions d'élèves"
    row = fetch_one("SELECT COUNT(*) AS n FROM seance WHERE sequence_id = ?", (sequence_id,))
    if row and int(row["n"]) > 0:
        return "des séances liées (supprimez-les d'abord)"
    return None


def bulk_delete_sequences(ids):
    """Supprime plusieurs enregistrements par ID. Aucune concaténation SQL."""
    if not ids:
        return
    placeholders = ", ".join("?" for _ in ids)
    execute("DELETE FROM sequence WHERE Id IN (" + placeholders + ")", list(ids))


_SEARCH_COLS  = ['sequence.Identifiant', 'sequence.Titre', 'sequence.Presentation', 'sequence.Statut']
_ALLOWED_SORT = {"identifiant": "sequence.Identifiant", "titre": "sequence.Titre", "presentation": "sequence.Presentation", "statut": "sequence.Statut", "activite_glissante": "sequence.ActiviteGlissante", "ordre_impose": "sequence.OrdreImpose", "niveau_classe_id": "sequence.niveau_classe_id", "id": "sequence.Id"}
_ALLOWED_FILTERS = {"niveau_classe_id": "sequence.niveau_classe_id"}
_DEFAULT_SORT = "sequence.Id"


def count_sequences(q: str | None = None, filters: dict[str, Any] | None = None) -> int:
    clauses: list[str] = []
    params: list[Any] = []
    if q and _SEARCH_COLS:
        clauses.append("(" + " OR ".join(c + " LIKE ?" for c in _SEARCH_COLS) + ")")
        params.extend("%" + q + "%" for _ in _SEARCH_COLS)
    for key, val in (filters or {}).items():
        if val is not None and val != "":
            col = _ALLOWED_FILTERS.get(key)
            if col is None:
                raise ValueError(f"Filtre interdit : {key}")
            clauses.append(col + " = ?")
            params.append(val)
    if clauses:
        sql = "SELECT COUNT(*) AS total FROM sequence WHERE " + " AND ".join(clauses)
    else:
        sql = "SELECT COUNT(*) AS total FROM sequence"
    row = fetch_one(sql, params)
    return row["total"] if row else 0


def find_sequences_paginated(q: str | None = None, sort: str | None = None, direction: str = "asc", limit: int = 10, offset: int = 0, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    sort_col = _ALLOWED_SORT.get(sort or "", _DEFAULT_SORT)
    sort_dir = "DESC" if direction == "desc" else "ASC"
    base = "SELECT sequence.*, niveau_classe.Code AS niveau_classe_id_label FROM sequence LEFT JOIN niveau_classe ON sequence.niveau_classe_id = niveau_classe.Id"
    clauses: list[str] = []
    params: list[Any] = []
    if q and _SEARCH_COLS:
        clauses.append("(" + " OR ".join(c + " LIKE ?" for c in _SEARCH_COLS) + ")")
        params.extend("%" + q + "%" for _ in _SEARCH_COLS)
    for key, val in (filters or {}).items():
        if val is not None and val != "":
            col = _ALLOWED_FILTERS.get(key)
            if col is None:
                raise ValueError(f"Filtre interdit : {key}")
            clauses.append(col + " = ?")
            params.append(val)
    if clauses:
        sql = base + " WHERE " + " AND ".join(clauses) + " ORDER BY " + sort_col + " " + sort_dir + " LIMIT ? OFFSET ?"
    else:
        sql = base + " ORDER BY " + sort_col + " " + sort_dir + " LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    return fetch_all(sql, params)



_EXPORT_LIMIT = 1000


def find_sequences_for_export(q: str | None = None, sort: str | None = None, direction: str = "asc", filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    return find_sequences_paginated(
        q=q, sort=sort, direction=direction,
        limit=_EXPORT_LIMIT, offset=0, filters=filters,
    )



def get_niveau_classe_choices():
    """Liste générique (séquences HORS référentiel) : intitulé lisible."""
    rows = fetch_all("SELECT Id, Intitule FROM niveau_classe ORDER BY Intitule")
    return [(row["Id"], row["Intitule"]) for row in rows]


def get_niveau_choices_pour_referentiel(referentiel_id):
    """Niveaux possibles pour une séquence ADOSSÉE à un référentiel (ADR-023) :
    les FormationNiveau de la formation du référentiel — ex. 2TNE-CIEL n'offre
    que « 2TNE — Seconde ». La valeur stockée reste niveau_classe_id (le
    rattachement de la séquence à FormationNiveau est un raffinement ultérieur,
    hors ADR-023)."""
    rows = fetch_all(
        "SELECT fn.niveau_classe_id AS Id, fn.Libelle FROM formation_niveau fn "
        "JOIN referentiel_niveau_classe r ON r.formation_id = fn.formation_id "
        "WHERE r.Id = ? ORDER BY fn.OrdreIndicatif, fn.Libelle",
        (referentiel_id,),
    )
    return [(row["Id"], row["Libelle"]) for row in rows]


def titre_existe_autre(titre, sauf_id):
    """Le titre est-il déjà porté par une AUTRE séquence ? (unicité, garde au renommage)."""
    return fetch_one(
        "SELECT 1 AS x FROM sequence WHERE Titre = ? AND Id <> ? LIMIT 1",
        (titre, sauf_id),
    ) is not None
