from typing import Any

from core.database.db import fetch_one, fetch_all, execute, insert

SELECT_ALL   = "SELECT * FROM professeur ORDER BY Id"
SELECT_BY_ID = "SELECT * FROM professeur WHERE Id = ?"
INSERT       = "INSERT INTO professeur (Nom, Prenom, UserId) VALUES (?, ?, ?)"
UPDATE       = "UPDATE professeur SET Nom = ?, Prenom = ?, UserId = ? WHERE Id = ?"
DELETE       = "DELETE FROM professeur WHERE Id = ?"


def get_professeurs():
    return fetch_all(SELECT_ALL)


def get_professeur_by_id(id):
    return fetch_one(SELECT_BY_ID, (id,))


def add_professeur(data):
    return insert(INSERT, (data["nom"], data["prenom"], data["user_id"], ))


def update_professeur(id, data):
    execute(UPDATE, (data["nom"], data["prenom"], data["user_id"], id))


def delete_professeur(id):
    execute(DELETE, (id,))


def bulk_delete_professeurs(ids):
    """Supprime plusieurs enregistrements par ID. Aucune concaténation SQL."""
    if not ids:
        return
    placeholders = ", ".join("?" for _ in ids)
    execute("DELETE FROM professeur WHERE Id IN (" + placeholders + ")", list(ids))


_SEARCH_COLS  = ['Nom', 'Prenom']
_ALLOWED_SORT = {"nom": "Nom", "prenom": "Prenom", "user_id": "UserId", "created_at": "CreatedAt", "updated_at": "UpdatedAt", "id": "Id"}
_ALLOWED_FILTERS = {}
_DEFAULT_SORT = "Id"


def count_professeurs(q: str | None = None, filters: dict[str, Any] | None = None) -> int:
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
        sql = "SELECT COUNT(*) AS total FROM professeur WHERE " + " AND ".join(clauses)
    else:
        sql = "SELECT COUNT(*) AS total FROM professeur"
    row = fetch_one(sql, params)
    return row["total"] if row else 0


def find_professeurs_paginated(q: str | None = None, sort: str | None = None, direction: str = "asc", limit: int = 10, offset: int = 0, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    sort_col = _ALLOWED_SORT.get(sort or "", _DEFAULT_SORT)
    sort_dir = "DESC" if direction == "desc" else "ASC"
    base = "SELECT * FROM professeur"
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


def find_professeurs_for_export(q: str | None = None, sort: str | None = None, direction: str = "asc", filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    return find_professeurs_paginated(
        q=q, sort=sort, direction=direction,
        limit=_EXPORT_LIMIT, offset=0, filters=filters,
    )
