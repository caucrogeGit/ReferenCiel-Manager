from datetime import datetime, timezone

from typing import Any

from core.database.db import fetch_one, fetch_all, execute, insert

SELECT_ALL   = "SELECT version_starter.*, starter_welcome.Titre AS starter_id_label FROM version_starter LEFT JOIN starter_welcome ON version_starter.starter_id = starter_welcome.Id ORDER BY version_starter.Id"
SELECT_BY_ID = "SELECT version_starter.*, starter_welcome.Titre AS starter_id_label FROM version_starter LEFT JOIN starter_welcome ON version_starter.starter_id = starter_welcome.Id WHERE version_starter.Id = ?"
INSERT       = "INSERT INTO version_starter (Version, Statut, ActiviteGlissante, OrdreImpose, starter_id, CreatedAt, UpdatedAt) VALUES (?, ?, ?, ?, ?, ?, ?)"
UPDATE       = "UPDATE version_starter SET Version = ?, Statut = ?, ActiviteGlissante = ?, OrdreImpose = ?, starter_id = ?, UpdatedAt = ? WHERE Id = ?"
DELETE       = "DELETE FROM version_starter WHERE Id = ?"


def get_version_starters():
    return fetch_all(SELECT_ALL)


def get_version_starter_by_id(id):
    return fetch_one(SELECT_BY_ID, (id,))


def add_version_starter(data):
    return insert(INSERT, (data["version"], data["statut"], data["activite_glissante"], data["ordre_impose"], data["starter_id"], datetime.now(timezone.utc), datetime.now(timezone.utc),))


def update_version_starter(id, data):
    execute(UPDATE, (data["version"], data["statut"], data["activite_glissante"], data["ordre_impose"], data["starter_id"], datetime.now(timezone.utc), id))


def delete_version_starter(id):
    execute(DELETE, (id,))


def bulk_delete_version_starters(ids):
    """Supprime plusieurs enregistrements par ID. Aucune concaténation SQL."""
    if not ids:
        return
    placeholders = ", ".join("?" for _ in ids)
    execute("DELETE FROM version_starter WHERE Id IN (" + placeholders + ")", list(ids))


_SEARCH_COLS  = ['version_starter.Version', 'version_starter.Statut']
_ALLOWED_SORT = {"version": "version_starter.Version", "statut": "version_starter.Statut", "activite_glissante": "version_starter.ActiviteGlissante", "ordre_impose": "version_starter.OrdreImpose", "starter_id": "version_starter.starter_id", "created_at": "version_starter.CreatedAt", "updated_at": "version_starter.UpdatedAt", "id": "version_starter.Id"}
_ALLOWED_FILTERS = {"starter_id": "version_starter.starter_id"}
_DEFAULT_SORT = "version_starter.Id"


def count_version_starters(q: str | None = None, filters: dict[str, Any] | None = None) -> int:
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
        sql = "SELECT COUNT(*) AS total FROM version_starter WHERE " + " AND ".join(clauses)
    else:
        sql = "SELECT COUNT(*) AS total FROM version_starter"
    row = fetch_one(sql, params)
    return row["total"] if row else 0


def find_version_starters_paginated(q: str | None = None, sort: str | None = None, direction: str = "asc", limit: int = 10, offset: int = 0, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    sort_col = _ALLOWED_SORT.get(sort or "", _DEFAULT_SORT)
    sort_dir = "DESC" if direction == "desc" else "ASC"
    base = "SELECT version_starter.*, starter_welcome.Titre AS starter_id_label FROM version_starter LEFT JOIN starter_welcome ON version_starter.starter_id = starter_welcome.Id"
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


def find_version_starters_for_export(q: str | None = None, sort: str | None = None, direction: str = "asc", filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    return find_version_starters_paginated(
        q=q, sort=sort, direction=direction,
        limit=_EXPORT_LIMIT, offset=0, filters=filters,
    )



def get_starter_welcome_choices():
    rows = fetch_all("SELECT Id, Titre FROM starter_welcome ORDER BY Titre")
    return [(row["Id"], row["Titre"]) for row in rows]