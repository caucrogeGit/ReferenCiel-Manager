from datetime import datetime, timezone

from typing import Any

from core.database.db import fetch_one, fetch_all, execute, insert

SELECT_ALL   = "SELECT progression_seance.*, progression_parcours.Statut AS progression_parcours_id_label, seance.Titre AS seance_id_label FROM progression_seance LEFT JOIN progression_parcours ON progression_seance.progression_parcours_id = progression_parcours.Id LEFT JOIN seance ON progression_seance.seance_id = seance.Id ORDER BY progression_seance.Id"
SELECT_BY_ID = "SELECT progression_seance.*, progression_parcours.Statut AS progression_parcours_id_label, seance.Titre AS seance_id_label FROM progression_seance LEFT JOIN progression_parcours ON progression_seance.progression_parcours_id = progression_parcours.Id LEFT JOIN seance ON progression_seance.seance_id = seance.Id WHERE progression_seance.Id = ?"
INSERT       = "INSERT INTO progression_seance (Statut, progression_parcours_id, seance_id, CreatedAt, UpdatedAt) VALUES (?, ?, ?, ?, ?)"
UPDATE       = "UPDATE progression_seance SET Statut = ?, progression_parcours_id = ?, seance_id = ?, UpdatedAt = ? WHERE Id = ?"
DELETE       = "DELETE FROM progression_seance WHERE Id = ?"


def get_progression_seances():
    return fetch_all(SELECT_ALL)


def get_progression_seance_by_id(id):
    return fetch_one(SELECT_BY_ID, (id,))


def add_progression_seance(data):
    return insert(INSERT, (data["statut"], data["progression_parcours_id"], data["seance_id"], datetime.now(timezone.utc), datetime.now(timezone.utc),))


def update_progression_seance(id, data):
    execute(UPDATE, (data["statut"], data["progression_parcours_id"], data["seance_id"], datetime.now(timezone.utc), id))


def delete_progression_seance(id):
    execute(DELETE, (id,))


def bulk_delete_progression_seances(ids):
    """Supprime plusieurs enregistrements par ID. Aucune concaténation SQL."""
    if not ids:
        return
    placeholders = ", ".join("?" for _ in ids)
    execute("DELETE FROM progression_seance WHERE Id IN (" + placeholders + ")", list(ids))


_SEARCH_COLS  = ['progression_seance.Statut']
_ALLOWED_SORT = {"statut": "progression_seance.Statut", "progression_parcours_id": "progression_seance.progression_parcours_id", "seance_id": "progression_seance.seance_id", "created_at": "progression_seance.CreatedAt", "updated_at": "progression_seance.UpdatedAt", "id": "progression_seance.Id"}
_ALLOWED_FILTERS = {"progression_parcours_id": "progression_seance.progression_parcours_id", "seance_id": "progression_seance.seance_id"}
_DEFAULT_SORT = "progression_seance.Id"


def count_progression_seances(q: str | None = None, filters: dict[str, Any] | None = None) -> int:
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
        sql = "SELECT COUNT(*) AS total FROM progression_seance WHERE " + " AND ".join(clauses)
    else:
        sql = "SELECT COUNT(*) AS total FROM progression_seance"
    row = fetch_one(sql, params)
    return row["total"] if row else 0


def find_progression_seances_paginated(q: str | None = None, sort: str | None = None, direction: str = "asc", limit: int = 10, offset: int = 0, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    sort_col = _ALLOWED_SORT.get(sort or "", _DEFAULT_SORT)
    sort_dir = "DESC" if direction == "desc" else "ASC"
    base = "SELECT progression_seance.*, progression_parcours.Statut AS progression_parcours_id_label, seance.Titre AS seance_id_label FROM progression_seance LEFT JOIN progression_parcours ON progression_seance.progression_parcours_id = progression_parcours.Id LEFT JOIN seance ON progression_seance.seance_id = seance.Id"
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


def find_progression_seances_for_export(q: str | None = None, sort: str | None = None, direction: str = "asc", filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    return find_progression_seances_paginated(
        q=q, sort=sort, direction=direction,
        limit=_EXPORT_LIMIT, offset=0, filters=filters,
    )



def get_progression_parcours_choices():
    rows = fetch_all("SELECT Id, Statut FROM progression_parcours ORDER BY Statut")
    return [(row["Id"], row["Statut"]) for row in rows]


def get_seance_choices():
    rows = fetch_all("SELECT Id, Titre FROM seance ORDER BY Titre")
    return [(row["Id"], row["Titre"]) for row in rows]