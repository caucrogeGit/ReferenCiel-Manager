from datetime import datetime, timezone

from typing import Any

from core.database.db import fetch_one, fetch_all, execute, insert

SELECT_ALL   = "SELECT item_checklist.*, section_checklist.Titre AS section_id_label FROM item_checklist LEFT JOIN section_checklist ON item_checklist.section_id = section_checklist.Id ORDER BY item_checklist.Id"
SELECT_BY_ID = "SELECT item_checklist.*, section_checklist.Titre AS section_id_label FROM item_checklist LEFT JOIN section_checklist ON item_checklist.section_id = section_checklist.Id WHERE item_checklist.Id = ?"
INSERT       = "INSERT INTO item_checklist (Libelle, section_id, CreatedAt, UpdatedAt) VALUES (?, ?, ?, ?)"
UPDATE       = "UPDATE item_checklist SET Libelle = ?, section_id = ?, UpdatedAt = ? WHERE Id = ?"
DELETE       = "DELETE FROM item_checklist WHERE Id = ?"


def get_item_checklists():
    return fetch_all(SELECT_ALL)


def get_item_checklist_by_id(id):
    return fetch_one(SELECT_BY_ID, (id,))


def add_item_checklist(data):
    return insert(INSERT, (data["libelle"], data["section_id"], datetime.now(timezone.utc), datetime.now(timezone.utc),))


def update_item_checklist(id, data):
    execute(UPDATE, (data["libelle"], data["section_id"], datetime.now(timezone.utc), id))


def delete_item_checklist(id):
    execute(DELETE, (id,))


def bulk_delete_item_checklists(ids):
    """Supprime plusieurs enregistrements par ID. Aucune concaténation SQL."""
    if not ids:
        return
    placeholders = ", ".join("?" for _ in ids)
    execute("DELETE FROM item_checklist WHERE Id IN (" + placeholders + ")", list(ids))


_SEARCH_COLS  = ['item_checklist.Libelle']
_ALLOWED_SORT = {"libelle": "item_checklist.Libelle", "section_id": "item_checklist.section_id", "created_at": "item_checklist.CreatedAt", "updated_at": "item_checklist.UpdatedAt", "id": "item_checklist.Id"}
_ALLOWED_FILTERS = {"section_id": "item_checklist.section_id"}
_DEFAULT_SORT = "item_checklist.Id"


def count_item_checklists(q: str | None = None, filters: dict[str, Any] | None = None) -> int:
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
        sql = "SELECT COUNT(*) AS total FROM item_checklist WHERE " + " AND ".join(clauses)
    else:
        sql = "SELECT COUNT(*) AS total FROM item_checklist"
    row = fetch_one(sql, params)
    return row["total"] if row else 0


def find_item_checklists_paginated(q: str | None = None, sort: str | None = None, direction: str = "asc", limit: int = 10, offset: int = 0, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    sort_col = _ALLOWED_SORT.get(sort or "", _DEFAULT_SORT)
    sort_dir = "DESC" if direction == "desc" else "ASC"
    base = "SELECT item_checklist.*, section_checklist.Titre AS section_id_label FROM item_checklist LEFT JOIN section_checklist ON item_checklist.section_id = section_checklist.Id"
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


def find_item_checklists_for_export(q: str | None = None, sort: str | None = None, direction: str = "asc", filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    return find_item_checklists_paginated(
        q=q, sort=sort, direction=direction,
        limit=_EXPORT_LIMIT, offset=0, filters=filters,
    )



def get_section_checklist_choices():
    rows = fetch_all("SELECT Id, Titre FROM section_checklist ORDER BY Titre")
    return [(row["Id"], row["Titre"]) for row in rows]