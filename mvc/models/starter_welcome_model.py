from typing import Any

from core.database.db import fetch_one, fetch_all, execute, insert

SELECT_ALL   = "SELECT starter_welcome.*, niveau_classe.Code AS niveau_classe_id_label FROM starter_welcome LEFT JOIN niveau_classe ON starter_welcome.niveau_classe_id = niveau_classe.Id ORDER BY starter_welcome.Id"
SELECT_BY_ID = "SELECT starter_welcome.*, niveau_classe.Code AS niveau_classe_id_label FROM starter_welcome LEFT JOIN niveau_classe ON starter_welcome.niveau_classe_id = niveau_classe.Id WHERE starter_welcome.Id = ?"
INSERT       = "INSERT INTO starter_welcome (Identifiant, Titre, Presentation, niveau_classe_id, CreatedAt, UpdatedAt) VALUES (?, ?, ?, ?, ?, ?)"
UPDATE       = "UPDATE starter_welcome SET Identifiant = ?, Titre = ?, Presentation = ?, niveau_classe_id = ?, CreatedAt = ?, UpdatedAt = ? WHERE Id = ?"
DELETE       = "DELETE FROM starter_welcome WHERE Id = ?"


def get_starter_welcomes():
    return fetch_all(SELECT_ALL)


def get_starter_welcome_by_id(id):
    return fetch_one(SELECT_BY_ID, (id,))


def add_starter_welcome(data):
    return insert(INSERT, (data["identifiant"], data["titre"], data["presentation"], data["niveau_classe_id"], data["created_at"], data["updated_at"],))


def update_starter_welcome(id, data):
    execute(UPDATE, (data["identifiant"], data["titre"], data["presentation"], data["niveau_classe_id"], data["created_at"], data["updated_at"], id))


def delete_starter_welcome(id):
    execute(DELETE, (id,))


def bulk_delete_starter_welcomes(ids):
    """Supprime plusieurs enregistrements par ID. Aucune concaténation SQL."""
    if not ids:
        return
    placeholders = ", ".join("?" for _ in ids)
    execute("DELETE FROM starter_welcome WHERE Id IN (" + placeholders + ")", list(ids))


_SEARCH_COLS  = ['starter_welcome.Identifiant', 'starter_welcome.Titre', 'starter_welcome.Presentation']
_ALLOWED_SORT = {"identifiant": "starter_welcome.Identifiant", "titre": "starter_welcome.Titre", "presentation": "starter_welcome.Presentation", "niveau_classe_id": "starter_welcome.niveau_classe_id", "created_at": "starter_welcome.CreatedAt", "updated_at": "starter_welcome.UpdatedAt", "id": "starter_welcome.Id"}
_ALLOWED_FILTERS = {"niveau_classe_id": "starter_welcome.niveau_classe_id"}
_DEFAULT_SORT = "starter_welcome.Id"


def count_starter_welcomes(q: str | None = None, filters: dict[str, Any] | None = None) -> int:
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
        sql = "SELECT COUNT(*) AS total FROM starter_welcome WHERE " + " AND ".join(clauses)
    else:
        sql = "SELECT COUNT(*) AS total FROM starter_welcome"
    row = fetch_one(sql, params)
    return row["total"] if row else 0


def find_starter_welcomes_paginated(q: str | None = None, sort: str | None = None, direction: str = "asc", limit: int = 10, offset: int = 0, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    sort_col = _ALLOWED_SORT.get(sort or "", _DEFAULT_SORT)
    sort_dir = "DESC" if direction == "desc" else "ASC"
    base = "SELECT starter_welcome.*, niveau_classe.Code AS niveau_classe_id_label FROM starter_welcome LEFT JOIN niveau_classe ON starter_welcome.niveau_classe_id = niveau_classe.Id"
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


def find_starter_welcomes_for_export(q: str | None = None, sort: str | None = None, direction: str = "asc", filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    return find_starter_welcomes_paginated(
        q=q, sort=sort, direction=direction,
        limit=_EXPORT_LIMIT, offset=0, filters=filters,
    )



def get_niveau_classe_choices():
    rows = fetch_all("SELECT Id, Code FROM niveau_classe ORDER BY Code")
    return [(row["Id"], row["Code"]) for row in rows]