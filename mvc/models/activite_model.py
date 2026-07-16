from datetime import datetime, timezone

from typing import Any

from core.database.db import fetch_one, fetch_all, execute, insert

SELECT_ALL   = "SELECT activite.*, seance.Titre AS palier_id_label FROM activite LEFT JOIN seance ON activite.seance_id = seance.Id ORDER BY activite.Id"
SELECT_BY_ID = "SELECT activite.*, seance.Titre AS palier_id_label FROM activite LEFT JOIN seance ON activite.seance_id = seance.Id WHERE activite.Id = ?"
INSERT       = "INSERT INTO activite (Objectif, Fichier, seance_id, CreatedAt, UpdatedAt) VALUES (?, ?, ?, ?, ?)"
UPDATE       = "UPDATE activite SET Objectif = ?, Fichier = ?, seance_id = ?, UpdatedAt = ? WHERE Id = ?"
DELETE       = "DELETE FROM activite WHERE Id = ?"


def get_activites():
    return fetch_all(SELECT_ALL)


def get_activite_by_id(id):
    return fetch_one(SELECT_BY_ID, (id,))


def add_activite(data):
    return insert(INSERT, (data["objectif"], data["fichier"], data["seance_id"], datetime.now(timezone.utc), datetime.now(timezone.utc),))


def update_activite(id, data):
    execute(UPDATE, (data["objectif"], data["fichier"], data["seance_id"], datetime.now(timezone.utc), id))


def delete_activite(id):
    execute(DELETE, (id,))


def bulk_delete_activites(ids):
    """Supprime plusieurs enregistrements par ID. Aucune concaténation SQL."""
    if not ids:
        return
    placeholders = ", ".join("?" for _ in ids)
    execute("DELETE FROM activite WHERE Id IN (" + placeholders + ")", list(ids))


_SEARCH_COLS  = ['activite.Objectif', 'activite.Fichier']
_ALLOWED_SORT = {"objectif": "activite.Objectif", "fichier": "activite.Fichier", "seance_id": "activite.seance_id", "created_at": "activite.CreatedAt", "updated_at": "activite.UpdatedAt", "id": "activite.Id"}
_ALLOWED_FILTERS = {"seance_id": "activite.seance_id"}
_DEFAULT_SORT = "activite.Id"


def count_activites(q: str | None = None, filters: dict[str, Any] | None = None) -> int:
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
        sql = "SELECT COUNT(*) AS total FROM activite WHERE " + " AND ".join(clauses)
    else:
        sql = "SELECT COUNT(*) AS total FROM activite"
    row = fetch_one(sql, params)
    return row["total"] if row else 0


def find_activites_paginated(q: str | None = None, sort: str | None = None, direction: str = "asc", limit: int = 10, offset: int = 0, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    sort_col = _ALLOWED_SORT.get(sort or "", _DEFAULT_SORT)
    sort_dir = "DESC" if direction == "desc" else "ASC"
    base = "SELECT activite.*, seance.Titre AS palier_id_label FROM activite LEFT JOIN seance ON activite.seance_id = seance.Id"
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


def find_activites_for_export(q: str | None = None, sort: str | None = None, direction: str = "asc", filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    return find_activites_paginated(
        q=q, sort=sort, direction=direction,
        limit=_EXPORT_LIMIT, offset=0, filters=filters,
    )



def get_palier_choices():
    rows = fetch_all("SELECT Id, Titre FROM seance ORDER BY Titre")
    return [(row["Id"], row["Titre"]) for row in rows]