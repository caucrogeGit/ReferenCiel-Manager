from typing import Any

from core.database.db import fetch_one, fetch_all, execute, insert

SELECT_ALL   = "SELECT checklist.*, palier.Titre AS palier_id_label FROM checklist LEFT JOIN palier ON checklist.palier_id = palier.Id ORDER BY checklist.Id"
SELECT_BY_ID = "SELECT checklist.*, palier.Titre AS palier_id_label FROM checklist LEFT JOIN palier ON checklist.palier_id = palier.Id WHERE checklist.Id = ?"
INSERT       = "INSERT INTO checklist (DecisionFinale, palier_id) VALUES (?, ?)"
UPDATE       = "UPDATE checklist SET DecisionFinale = ?, palier_id = ? WHERE Id = ?"
DELETE       = "DELETE FROM checklist WHERE Id = ?"


def get_checklists():
    return fetch_all(SELECT_ALL)


def get_checklist_by_id(id):
    return fetch_one(SELECT_BY_ID, (id,))


def add_checklist(data):
    return insert(INSERT, (data["decision_finale"], data["palier_id"], ))


def update_checklist(id, data):
    execute(UPDATE, (data["decision_finale"], data["palier_id"], id))


def delete_checklist(id):
    execute(DELETE, (id,))


def bulk_delete_checklists(ids):
    """Supprime plusieurs enregistrements par ID. Aucune concaténation SQL."""
    if not ids:
        return
    placeholders = ", ".join("?" for _ in ids)
    execute("DELETE FROM checklist WHERE Id IN (" + placeholders + ")", list(ids))


_SEARCH_COLS  = ['checklist.DecisionFinale']
_ALLOWED_SORT = {"decision_finale": "checklist.DecisionFinale", "palier_id": "checklist.palier_id", "created_at": "checklist.CreatedAt", "updated_at": "checklist.UpdatedAt", "id": "checklist.Id"}
_ALLOWED_FILTERS = {"palier_id": "checklist.palier_id"}
_DEFAULT_SORT = "checklist.Id"


def count_checklists(q: str | None = None, filters: dict[str, Any] | None = None) -> int:
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
        sql = "SELECT COUNT(*) AS total FROM checklist WHERE " + " AND ".join(clauses)
    else:
        sql = "SELECT COUNT(*) AS total FROM checklist"
    row = fetch_one(sql, params)
    return row["total"] if row else 0


def find_checklists_paginated(q: str | None = None, sort: str | None = None, direction: str = "asc", limit: int = 10, offset: int = 0, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    sort_col = _ALLOWED_SORT.get(sort or "", _DEFAULT_SORT)
    sort_dir = "DESC" if direction == "desc" else "ASC"
    base = "SELECT checklist.*, palier.Titre AS palier_id_label FROM checklist LEFT JOIN palier ON checklist.palier_id = palier.Id"
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


def find_checklists_for_export(q: str | None = None, sort: str | None = None, direction: str = "asc", filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    return find_checklists_paginated(
        q=q, sort=sort, direction=direction,
        limit=_EXPORT_LIMIT, offset=0, filters=filters,
    )



def get_palier_choices():
    rows = fetch_all("SELECT Id, Titre FROM palier ORDER BY Titre")
    return [(row["Id"], row["Titre"]) for row in rows]