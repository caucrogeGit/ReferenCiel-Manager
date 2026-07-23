from datetime import datetime, timezone

from typing import Any

from core.database.db import fetch_one, fetch_all, execute, insert
from mvc.services.sequence_tunnel import statuts_ouvrants_pour_nature

# nb_progressions alimente l'état du bouton Supprimer des cartes (une séance
# avec progressions d'élèves est protégée en RESTRICT au contrat).
SELECT_ALL   = (
    "SELECT seance.*, sequence.Titre AS sequence_id_label, "
    "(SELECT COUNT(*) FROM progression_seance pp WHERE pp.seance_id = seance.Id) AS nb_progressions "
    "FROM seance LEFT JOIN sequence ON seance.sequence_id = sequence.Id "
    "ORDER BY sequence.Titre, seance.Ordre, seance.Id"
)
SELECT_BY_ID = "SELECT seance.*, sequence.Titre AS sequence_id_label, sequence.Nature AS sequence_nature, sequence.Statut AS sequence_statut FROM seance LEFT JOIN sequence ON seance.sequence_id = sequence.Id WHERE seance.Id = ?"
INSERT       = "INSERT INTO seance (Ordre, Titre, Theme, ProductionAttendue, ObjectifOperationnel, ConsigneGenerale, DureeEstimeeMinutes, Prerequis, ModalitePedagogique, ConditionRealisation, ConditionValidation, Remediation, sequence_id, CreatedAt, UpdatedAt) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
UPDATE       = "UPDATE seance SET Ordre = ?, Titre = ?, Theme = ?, ProductionAttendue = ?, ObjectifOperationnel = ?, ConsigneGenerale = ?, DureeEstimeeMinutes = ?, Prerequis = ?, ModalitePedagogique = ?, ConditionRealisation = ?, ConditionValidation = ?, Remediation = ?, sequence_id = ?, UpdatedAt = ? WHERE Id = ?"
DELETE       = "DELETE FROM seance WHERE Id = ?"


def get_seances():
    return fetch_all(SELECT_ALL)


def get_seance_by_id(id):
    return fetch_one(SELECT_BY_ID, (id,))


UPDATE_FICHE = ("UPDATE seance SET Ordre = ?, Titre = ?, Theme = ?, ProductionAttendue = ?, "
                "ObjectifOperationnel = ?, ConsigneGenerale = ?, DureeEstimeeMinutes = ?, Prerequis = ?, "
                "ModalitePedagogique = ?, ConditionRealisation = ?, ConditionValidation = ?, "
                "Remediation = ?, UpdatedAt = ? WHERE Id = ?")


def update_fiche(id, data):
    """Auto-save de l'étape Fiche du tunnel (champs de la séance, pas sequence_id)."""
    execute(UPDATE_FICHE, (data["ordre"], data["titre"], data["theme"], data["production_attendue"], data["objectif_operationnel"], data["consigne_generale"], data["duree_estimee_minutes"], data["prerequis"], data["modalite_pedagogique"], data["condition_realisation"], data["condition_validation"], data["remediation"], datetime.now(timezone.utc), id))


def duree_cumulee_minutes(sequence_id):
    """Cumul des durées estimées des séances de la séquence, en minutes.

    None si la séquence n'a aucune séance ou aucune durée renseignée : la durée
    de la séquence est une valeur DÉRIVÉE, jamais saisie (retour porteur).
    """
    row = fetch_one(
        "SELECT SUM(DureeEstimeeMinutes) AS total FROM seance WHERE sequence_id = ?",
        (sequence_id,),
    )
    return int(row["total"]) if row and row["total"] is not None else None


def prerequis_par_seance(sequence_id):
    """Prérequis renseignés sur les séances de la séquence, dans l'ordre.

    Le « Prérequis » d'une séquence est DÉRIVÉ de ses séances, jamais saisi
    (retour porteur) — comme sa durée estimée.
    """
    return fetch_all(
        "SELECT Ordre, Titre, Prerequis FROM seance "
        "WHERE sequence_id = ? AND Prerequis IS NOT NULL AND Prerequis <> '' "
        "ORDER BY Ordre, Id",
        (sequence_id,),
    )


def prochain_ordre(sequence_id):
    """Prochain numéro d'ordre dans la séquence (1 si elle n'a aucune séance)."""
    row = fetch_one(
        "SELECT COALESCE(MAX(Ordre), 0) + 1 AS suivant FROM seance WHERE sequence_id = ?",
        (sequence_id,),
    )
    return int(row["suivant"]) if row else 1


def add_seance(data):
    return insert(INSERT, (data["ordre"], data["titre"], data["theme"], data["production_attendue"], data["objectif_operationnel"], data["consigne_generale"], data["duree_estimee_minutes"], data["prerequis"], data["modalite_pedagogique"], data["condition_realisation"], data["condition_validation"], data["remediation"], data["sequence_id"], datetime.now(timezone.utc), datetime.now(timezone.utc),))


def update_seance(id, data):
    execute(UPDATE, (data["ordre"], data["titre"], data["theme"], data["production_attendue"], data["objectif_operationnel"], data["consigne_generale"], data["duree_estimee_minutes"], data["prerequis"], data["modalite_pedagogique"], data["condition_realisation"], data["condition_validation"], data["remediation"], data["sequence_id"], datetime.now(timezone.utc), id))


def delete_seance(id):
    execute(DELETE, (id,))


# Références en ON DELETE RESTRICT au contrat : leur présence bloque la
# suppression d'une séance (les contenus propres — éléments, compétences,
# dossier — partent, eux, en CASCADE).
_BLOCAGES_SUPPRESSION = (
    ("progression_seance", "des progressions d'élèves"),
    ("checklist", "une checklist"),
    ("activite", "des activités"),
)


def motif_blocage_suppression(seance_id):
    """Raison humaine empêchant la suppression (FK restrict), ou None si libre."""
    for table, libelle in _BLOCAGES_SUPPRESSION:
        row = fetch_one(
            "SELECT COUNT(*) AS n FROM " + table + " WHERE seance_id = ?",
            (seance_id,),
        )
        if row and int(row["n"]) > 0:
            return libelle
    return None


def bulk_delete_seances(ids):
    """Supprime plusieurs enregistrements par ID. Aucune concaténation SQL."""
    if not ids:
        return
    placeholders = ", ".join("?" for _ in ids)
    execute("DELETE FROM seance WHERE Id IN (" + placeholders + ")", list(ids))


_SEARCH_COLS  = ['seance.Titre', 'seance.Theme', 'seance.ProductionAttendue']
_ALLOWED_SORT = {"ordre": "seance.Ordre", "titre": "seance.Titre", "theme": "seance.Theme", "production_attendue": "seance.ProductionAttendue", "sequence_id": "seance.sequence_id", "id": "seance.Id"}
_ALLOWED_FILTERS = {"sequence_id": "seance.sequence_id"}
_DEFAULT_SORT = "seance.Id"


def count_seances(q: str | None = None, filters: dict[str, Any] | None = None) -> int:
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
        sql = "SELECT COUNT(*) AS total FROM seance WHERE " + " AND ".join(clauses)
    else:
        sql = "SELECT COUNT(*) AS total FROM seance"
    row = fetch_one(sql, params)
    return row["total"] if row else 0


def find_seances_paginated(q: str | None = None, sort: str | None = None, direction: str = "asc", limit: int = 10, offset: int = 0, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    sort_col = _ALLOWED_SORT.get(sort or "", _DEFAULT_SORT)
    sort_dir = "DESC" if direction == "desc" else "ASC"
    base = "SELECT seance.*, sequence.Titre AS sequence_id_label FROM seance LEFT JOIN sequence ON seance.sequence_id = sequence.Id"
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


def find_seances_for_export(q: str | None = None, sort: str | None = None, direction: str = "asc", filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    return find_seances_paginated(
        q=q, sort=sort, direction=direction,
        limit=_EXPORT_LIMIT, offset=0, filters=filters,
    )



def get_seances_by_sequence(sequence_id):
    """Séances d'une séquence, ordonnées, avec tout leur détail (pour l'export)."""
    return fetch_all("SELECT * FROM seance WHERE sequence_id = ? ORDER BY Ordre, Id", (sequence_id,))


def feuilles_famille(sequence_id: int, nature: "str | None") -> "list[dict[str, Any]]":
    """Séances pour l'arbre « Famille pédagogique », avec un booléen Finalise
    DÉRIVÉ (jamais persisté, même philosophie que les statuts ADR-034/037) :
    fiche titrée, au moins un savoir OUVRANT pour la nature de la séquence,
    une compétence observée et un élément de déroulé — les quatre étapes du
    tunnel de la séance."""
    ouvrants = statuts_ouvrants_pour_nature(nature)
    marqueurs = ", ".join("?" for _ in ouvrants)
    return fetch_all(
        "SELECT se.Id, se.Ordre, se.Titre, se.DureeEstimeeMinutes, "
        "(se.Titre IS NOT NULL AND se.Titre <> '' "
        " AND EXISTS(SELECT 1 FROM seance_connaissance sk WHERE sk.seance_id = se.Id "
        "            AND sk.NiveauCible IS NOT NULL AND sk.Statut IN (" + marqueurs + ")) "
        " AND EXISTS(SELECT 1 FROM seance_competence sc WHERE sc.seance_id = se.Id) "
        " AND EXISTS(SELECT 1 FROM element_seance el WHERE el.seance_id = se.Id)) AS Finalise "
        "FROM seance se WHERE se.sequence_id = ? ORDER BY se.Ordre, se.Id",
        (*ouvrants, sequence_id),
    )


def get_sequence_choices_liables():
    """Séquences auxquelles une séance peut se lier (ADR-034) : dès « finalise »
    (tunnel complet). La première séance liée fait d'ailleurs passer la séquence
    en « publie ». Sert la création inline et sa validation serveur."""
    rows = fetch_all(
        "SELECT Id, Titre FROM sequence WHERE Statut IN ('finalise', 'publie', 'attribue') ORDER BY Titre"
    )
    return [(row["Id"], row["Titre"]) for row in rows]


def get_sequence_choices():
    rows = fetch_all("SELECT Id, Titre FROM sequence ORDER BY Titre")
    return [(row["Id"], row["Titre"]) for row in rows]