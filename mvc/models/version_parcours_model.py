from typing import Any

from core.database.db import fetch_one, fetch_all, execute, insert

SELECT_ALL   = "SELECT version_parcours.*, parcours.Titre AS parcours_id_label FROM version_parcours LEFT JOIN parcours ON version_parcours.parcours_id = parcours.Id ORDER BY version_parcours.Id"
SELECT_BY_ID = "SELECT version_parcours.*, parcours.Titre AS parcours_id_label FROM version_parcours LEFT JOIN parcours ON version_parcours.parcours_id = parcours.Id WHERE version_parcours.Id = ?"
INSERT       = "INSERT INTO version_parcours (Version, Statut, parcours_id) VALUES (?, ?, ?)"
UPDATE       = "UPDATE version_parcours SET Version = ?, Statut = ?, parcours_id = ? WHERE Id = ?"
DELETE       = "DELETE FROM version_parcours WHERE Id = ?"


def get_version_parcourss():
    return fetch_all(SELECT_ALL)


def get_version_parcours_by_id(id):
    return fetch_one(SELECT_BY_ID, (id,))


def add_version_parcours(data):
    return insert(INSERT, (data["version"], data["statut"], data["parcours_id"], ))


def update_version_parcours(id, data):
    execute(UPDATE, (data["version"], data["statut"], data["parcours_id"], id))


def delete_version_parcours(id):
    execute(DELETE, (id,))


def bulk_delete_version_parcourss(ids):
    """Supprime plusieurs enregistrements par ID. Aucune concaténation SQL."""
    if not ids:
        return
    placeholders = ", ".join("?" for _ in ids)
    execute("DELETE FROM version_parcours WHERE Id IN (" + placeholders + ")", list(ids))


_SEARCH_COLS  = ['version_parcours.Version', 'version_parcours.Statut']
_ALLOWED_SORT = {"version": "version_parcours.Version", "statut": "version_parcours.Statut", "parcours_id": "version_parcours.parcours_id", "created_at": "version_parcours.CreatedAt", "updated_at": "version_parcours.UpdatedAt", "id": "version_parcours.Id"}
_ALLOWED_FILTERS = {"parcours_id": "version_parcours.parcours_id"}
_DEFAULT_SORT = "version_parcours.Id"


def count_version_parcourss(q: str | None = None, filters: dict[str, Any] | None = None) -> int:
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
        sql = "SELECT COUNT(*) AS total FROM version_parcours WHERE " + " AND ".join(clauses)
    else:
        sql = "SELECT COUNT(*) AS total FROM version_parcours"
    row = fetch_one(sql, params)
    return row["total"] if row else 0


def find_version_parcourss_paginated(q: str | None = None, sort: str | None = None, direction: str = "asc", limit: int = 10, offset: int = 0, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    sort_col = _ALLOWED_SORT.get(sort or "", _DEFAULT_SORT)
    sort_dir = "DESC" if direction == "desc" else "ASC"
    base = "SELECT version_parcours.*, parcours.Titre AS parcours_id_label FROM version_parcours LEFT JOIN parcours ON version_parcours.parcours_id = parcours.Id"
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


def find_version_parcourss_for_export(q: str | None = None, sort: str | None = None, direction: str = "asc", filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    return find_version_parcourss_paginated(
        q=q, sort=sort, direction=direction,
        limit=_EXPORT_LIMIT, offset=0, filters=filters,
    )



def get_parcours_choices():
    rows = fetch_all("SELECT Id, Titre FROM parcours ORDER BY Titre")
    return [(row["Id"], row["Titre"]) for row in rows]