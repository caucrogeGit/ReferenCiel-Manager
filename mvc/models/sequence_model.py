from datetime import datetime, timezone

from typing import Any

from core.database.db import fetch_one, fetch_all, execute, insert

SELECT_ALL   = "SELECT sequence.*, niveau_classe.Code AS niveau_classe_id_label FROM sequence LEFT JOIN niveau_classe ON sequence.niveau_classe_id = niveau_classe.Id ORDER BY sequence.Id"
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


UPDATE_IDENTITE = "UPDATE sequence SET Titre = ?, ActiviteGlissante = ?, OrdreImpose = ?, niveau_classe_id = ?, UpdatedAt = ? WHERE Id = ?"
UPDATE_CADRE    = "UPDATE sequence SET Prerequis = ?, PositionnementProgression = ?, DureeEstimee = ?, ModalitesEvaluation = ?, UpdatedAt = ? WHERE Id = ?"


def update_identite(id, data):
    """Auto-save de l'étape Titre du tunnel. L'Identifiant (technique, dérivé du
    titre à la création) n'est pas géré par le professeur : on n'y touche pas."""
    execute(UPDATE_IDENTITE, (data["titre"], data["activite_glissante"], data["ordre_impose"], data["niveau_classe_id"], datetime.now(timezone.utc), id))


def update_cadre(id, data):
    """Auto-save de l'étape Cadre institutionnel (colonnes SEQ-02 seulement)."""
    execute(UPDATE_CADRE, (data["prerequis"], data["positionnement_progression"], data["duree_estimee"], data["modalites_evaluation"], datetime.now(timezone.utc), id))


def delete_sequence(id):
    execute(DELETE, (id,))


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
    rows = fetch_all("SELECT Id, Code FROM niveau_classe ORDER BY Code")
    return [(row["Id"], row["Code"]) for row in rows]