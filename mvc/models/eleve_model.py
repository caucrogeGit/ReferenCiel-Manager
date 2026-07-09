from typing import Any

from core.database.db import fetch_one, fetch_all, execute, insert

SELECT_ALL   = "SELECT * FROM eleve ORDER BY Id"
SELECT_BY_ID = "SELECT * FROM eleve WHERE Id = ?"
INSERT       = "INSERT INTO eleve (Nom, Prenom, Identifiant, DateNaissance, UserId, CreatedAt, UpdatedAt) VALUES (?, ?, ?, ?, ?, ?, ?)"
UPDATE       = "UPDATE eleve SET Nom = ?, Prenom = ?, Identifiant = ?, DateNaissance = ?, UserId = ?, CreatedAt = ?, UpdatedAt = ? WHERE Id = ?"
DELETE       = "DELETE FROM eleve WHERE Id = ?"


def get_eleves():
    return fetch_all(SELECT_ALL)


def get_eleve_by_id(id):
    return fetch_one(SELECT_BY_ID, (id,))


def add_eleve(data):
    return insert(INSERT, (data["nom"], data["prenom"], data["identifiant"], data["date_naissance"], data["user_id"], data["created_at"], data["updated_at"],))


def update_eleve(id, data):
    execute(UPDATE, (data["nom"], data["prenom"], data["identifiant"], data["date_naissance"], data["user_id"], data["created_at"], data["updated_at"], id))


def delete_eleve(id):
    execute(DELETE, (id,))


def bulk_delete_eleves(ids):
    """Supprime plusieurs enregistrements par ID. Aucune concaténation SQL."""
    if not ids:
        return
    placeholders = ", ".join("?" for _ in ids)
    execute("DELETE FROM eleve WHERE Id IN (" + placeholders + ")", list(ids))


_SEARCH_COLS  = ['Nom', 'Prenom', 'Identifiant']
_ALLOWED_SORT = {"nom": "Nom", "prenom": "Prenom", "identifiant": "Identifiant", "date_naissance": "DateNaissance", "user_id": "UserId", "created_at": "CreatedAt", "updated_at": "UpdatedAt", "id": "Id"}
_ALLOWED_FILTERS = {}
_DEFAULT_SORT = "Id"


def count_eleves(q: str | None = None, filters: dict[str, Any] | None = None) -> int:
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
        sql = "SELECT COUNT(*) AS total FROM eleve WHERE " + " AND ".join(clauses)
    else:
        sql = "SELECT COUNT(*) AS total FROM eleve"
    row = fetch_one(sql, params)
    return row["total"] if row else 0


def find_eleves_paginated(q: str | None = None, sort: str | None = None, direction: str = "asc", limit: int = 10, offset: int = 0, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    sort_col = _ALLOWED_SORT.get(sort or "", _DEFAULT_SORT)
    sort_dir = "DESC" if direction == "desc" else "ASC"
    base = "SELECT * FROM eleve"
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


def find_eleves_for_export(q: str | None = None, sort: str | None = None, direction: str = "asc", filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    return find_eleves_paginated(
        q=q, sort=sort, direction=direction,
        limit=_EXPORT_LIMIT, offset=0, filters=filters,
    )
