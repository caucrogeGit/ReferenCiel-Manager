from datetime import datetime, timezone

from typing import Any

from core.database.db import fetch_one, fetch_all, execute, insert

SELECT_ALL   = "SELECT progression_palier.*, progression_parcours.Statut AS progression_parcours_id_label, seance.Titre AS palier_id_label FROM progression_palier LEFT JOIN progression_parcours ON progression_palier.progression_parcours_id = progression_parcours.Id LEFT JOIN seance ON progression_palier.seance_id = seance.Id ORDER BY progression_palier.Id"
SELECT_BY_ID = "SELECT progression_palier.*, progression_parcours.Statut AS progression_parcours_id_label, seance.Titre AS palier_id_label FROM progression_palier LEFT JOIN progression_parcours ON progression_palier.progression_parcours_id = progression_parcours.Id LEFT JOIN seance ON progression_palier.seance_id = seance.Id WHERE progression_palier.Id = ?"
INSERT       = "INSERT INTO progression_palier (Statut, progression_parcours_id, seance_id, CreatedAt, UpdatedAt) VALUES (?, ?, ?, ?, ?)"
UPDATE       = "UPDATE progression_palier SET Statut = ?, progression_parcours_id = ?, seance_id = ?, UpdatedAt = ? WHERE Id = ?"
DELETE       = "DELETE FROM progression_palier WHERE Id = ?"


def get_progression_paliers():
    return fetch_all(SELECT_ALL)


def get_progression_palier_by_id(id):
    return fetch_one(SELECT_BY_ID, (id,))


def add_progression_palier(data):
    return insert(INSERT, (data["statut"], data["progression_parcours_id"], data["seance_id"], datetime.now(timezone.utc), datetime.now(timezone.utc),))


def update_progression_palier(id, data):
    execute(UPDATE, (data["statut"], data["progression_parcours_id"], data["seance_id"], datetime.now(timezone.utc), id))


def delete_progression_palier(id):
    execute(DELETE, (id,))


def bulk_delete_progression_paliers(ids):
    """Supprime plusieurs enregistrements par ID. Aucune concaténation SQL."""
    if not ids:
        return
    placeholders = ", ".join("?" for _ in ids)
    execute("DELETE FROM progression_palier WHERE Id IN (" + placeholders + ")", list(ids))


_SEARCH_COLS  = ['progression_palier.Statut']
_ALLOWED_SORT = {"statut": "progression_palier.Statut", "progression_parcours_id": "progression_palier.progression_parcours_id", "seance_id": "progression_palier.seance_id", "created_at": "progression_palier.CreatedAt", "updated_at": "progression_palier.UpdatedAt", "id": "progression_palier.Id"}
_ALLOWED_FILTERS = {"progression_parcours_id": "progression_palier.progression_parcours_id", "seance_id": "progression_palier.seance_id"}
_DEFAULT_SORT = "progression_palier.Id"


def count_progression_paliers(q: str | None = None, filters: dict[str, Any] | None = None) -> int:
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
        sql = "SELECT COUNT(*) AS total FROM progression_palier WHERE " + " AND ".join(clauses)
    else:
        sql = "SELECT COUNT(*) AS total FROM progression_palier"
    row = fetch_one(sql, params)
    return row["total"] if row else 0


def find_progression_paliers_paginated(q: str | None = None, sort: str | None = None, direction: str = "asc", limit: int = 10, offset: int = 0, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    sort_col = _ALLOWED_SORT.get(sort or "", _DEFAULT_SORT)
    sort_dir = "DESC" if direction == "desc" else "ASC"
    base = "SELECT progression_palier.*, progression_parcours.Statut AS progression_parcours_id_label, seance.Titre AS palier_id_label FROM progression_palier LEFT JOIN progression_parcours ON progression_palier.progression_parcours_id = progression_parcours.Id LEFT JOIN seance ON progression_palier.seance_id = seance.Id"
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


def find_progression_paliers_for_export(q: str | None = None, sort: str | None = None, direction: str = "asc", filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    return find_progression_paliers_paginated(
        q=q, sort=sort, direction=direction,
        limit=_EXPORT_LIMIT, offset=0, filters=filters,
    )



def get_progression_parcours_choices():
    rows = fetch_all("SELECT Id, Statut FROM progression_parcours ORDER BY Statut")
    return [(row["Id"], row["Statut"]) for row in rows]


def get_palier_choices():
    rows = fetch_all("SELECT Id, Titre FROM seance ORDER BY Titre")
    return [(row["Id"], row["Titre"]) for row in rows]