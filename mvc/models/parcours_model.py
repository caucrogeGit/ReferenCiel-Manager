from typing import Any

from core.database.db import fetch_one, fetch_all, execute, insert

SELECT_ALL   = "SELECT parcours.*, version_starter.Version AS version_starter_id_label FROM parcours LEFT JOIN version_starter ON parcours.version_starter_id = version_starter.Id ORDER BY parcours.Id"
SELECT_BY_ID = "SELECT parcours.*, version_starter.Version AS version_starter_id_label FROM parcours LEFT JOIN version_starter ON parcours.version_starter_id = version_starter.Id WHERE parcours.Id = ?"
INSERT       = "INSERT INTO parcours (Titre, version_starter_id) VALUES (?, ?)"
UPDATE       = "UPDATE parcours SET Titre = ?, version_starter_id = ? WHERE Id = ?"
DELETE       = "DELETE FROM parcours WHERE Id = ?"


def get_parcourss():
    return fetch_all(SELECT_ALL)


def get_parcours_by_id(id):
    return fetch_one(SELECT_BY_ID, (id,))


def add_parcours(data):
    return insert(INSERT, (data["titre"], data["version_starter_id"], ))


def update_parcours(id, data):
    execute(UPDATE, (data["titre"], data["version_starter_id"], id))


def delete_parcours(id):
    execute(DELETE, (id,))


def bulk_delete_parcourss(ids):
    """Supprime plusieurs enregistrements par ID. Aucune concaténation SQL."""
    if not ids:
        return
    placeholders = ", ".join("?" for _ in ids)
    execute("DELETE FROM parcours WHERE Id IN (" + placeholders + ")", list(ids))


_SEARCH_COLS  = ['parcours.Titre']
_ALLOWED_SORT = {"titre": "parcours.Titre", "version_starter_id": "parcours.version_starter_id", "created_at": "parcours.CreatedAt", "updated_at": "parcours.UpdatedAt", "id": "parcours.Id"}
_ALLOWED_FILTERS = {"version_starter_id": "parcours.version_starter_id"}
_DEFAULT_SORT = "parcours.Id"


def count_parcourss(q: str | None = None, filters: dict[str, Any] | None = None) -> int:
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
        sql = "SELECT COUNT(*) AS total FROM parcours WHERE " + " AND ".join(clauses)
    else:
        sql = "SELECT COUNT(*) AS total FROM parcours"
    row = fetch_one(sql, params)
    return row["total"] if row else 0


def find_parcourss_paginated(q: str | None = None, sort: str | None = None, direction: str = "asc", limit: int = 10, offset: int = 0, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    sort_col = _ALLOWED_SORT.get(sort or "", _DEFAULT_SORT)
    sort_dir = "DESC" if direction == "desc" else "ASC"
    base = "SELECT parcours.*, version_starter.Version AS version_starter_id_label FROM parcours LEFT JOIN version_starter ON parcours.version_starter_id = version_starter.Id"
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


def find_parcourss_for_export(q: str | None = None, sort: str | None = None, direction: str = "asc", filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    return find_parcourss_paginated(
        q=q, sort=sort, direction=direction,
        limit=_EXPORT_LIMIT, offset=0, filters=filters,
    )



def get_version_starter_choices():
    rows = fetch_all("SELECT Id, Version FROM version_starter ORDER BY Version")
    return [(row["Id"], row["Version"]) for row in rows]