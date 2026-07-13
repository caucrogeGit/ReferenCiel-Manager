from typing import Any

from core.database.db import fetch_one, fetch_all, execute, insert

SELECT_ALL   = "SELECT * FROM formation ORDER BY Id"
SELECT_BY_ID = "SELECT * FROM formation WHERE Id = ?"
INSERT       = "INSERT INTO formation (Code, Intitule) VALUES (?, ?)"
UPDATE       = "UPDATE formation SET Code = ?, Intitule = ? WHERE Id = ?"
DELETE       = "DELETE FROM formation WHERE Id = ?"


def get_formations():
    return fetch_all(SELECT_ALL)


def get_formation_by_id(id):
    return fetch_one(SELECT_BY_ID, (id,))


def add_formation(data):
    return insert(INSERT, (data["code"], data["intitule"], ))


def update_formation(id, data):
    execute(UPDATE, (data["code"], data["intitule"], id))


def delete_formation(id):
    execute(DELETE, (id,))


def bulk_delete_formations(ids):
    """Supprime plusieurs enregistrements par ID. Aucune concaténation SQL."""
    if not ids:
        return
    placeholders = ", ".join("?" for _ in ids)
    execute("DELETE FROM formation WHERE Id IN (" + placeholders + ")", list(ids))


_SEARCH_COLS  = ['Code', 'Intitule']
_ALLOWED_SORT = {"code": "Code", "intitule": "Intitule", "created_at": "CreatedAt", "updated_at": "UpdatedAt", "id": "Id"}
_ALLOWED_FILTERS = {}
_DEFAULT_SORT = "Id"


def count_formations(q: str | None = None, filters: dict[str, Any] | None = None) -> int:
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
        sql = "SELECT COUNT(*) AS total FROM formation WHERE " + " AND ".join(clauses)
    else:
        sql = "SELECT COUNT(*) AS total FROM formation"
    row = fetch_one(sql, params)
    return row["total"] if row else 0


def find_formations_paginated(q: str | None = None, sort: str | None = None, direction: str = "asc", limit: int = 10, offset: int = 0, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    sort_col = _ALLOWED_SORT.get(sort or "", _DEFAULT_SORT)
    sort_dir = "DESC" if direction == "desc" else "ASC"
    base = "SELECT * FROM formation"
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


def find_formations_for_export(q: str | None = None, sort: str | None = None, direction: str = "asc", filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    return find_formations_paginated(
        q=q, sort=sort, direction=direction,
        limit=_EXPORT_LIMIT, offset=0, filters=filters,
    )
