from typing import Any

from core.database.db import fetch_one, fetch_all, execute, insert

SELECT_ALL   = "SELECT section_checklist.*, checklist.DecisionFinale AS checklist_id_label FROM section_checklist LEFT JOIN checklist ON section_checklist.checklist_id = checklist.Id ORDER BY section_checklist.Id"
SELECT_BY_ID = "SELECT section_checklist.*, checklist.DecisionFinale AS checklist_id_label FROM section_checklist LEFT JOIN checklist ON section_checklist.checklist_id = checklist.Id WHERE section_checklist.Id = ?"
INSERT       = "INSERT INTO section_checklist (Numero, Titre, checklist_id, CreatedAt, UpdatedAt) VALUES (?, ?, ?, ?, ?)"
UPDATE       = "UPDATE section_checklist SET Numero = ?, Titre = ?, checklist_id = ?, CreatedAt = ?, UpdatedAt = ? WHERE Id = ?"
DELETE       = "DELETE FROM section_checklist WHERE Id = ?"


def get_section_checklists():
    return fetch_all(SELECT_ALL)


def get_section_checklist_by_id(id):
    return fetch_one(SELECT_BY_ID, (id,))


def add_section_checklist(data):
    return insert(INSERT, (data["numero"], data["titre"], data["checklist_id"], data["created_at"], data["updated_at"],))


def update_section_checklist(id, data):
    execute(UPDATE, (data["numero"], data["titre"], data["checklist_id"], data["created_at"], data["updated_at"], id))


def delete_section_checklist(id):
    execute(DELETE, (id,))


def bulk_delete_section_checklists(ids):
    """Supprime plusieurs enregistrements par ID. Aucune concaténation SQL."""
    if not ids:
        return
    placeholders = ", ".join("?" for _ in ids)
    execute("DELETE FROM section_checklist WHERE Id IN (" + placeholders + ")", list(ids))


_SEARCH_COLS  = ['section_checklist.Titre']
_ALLOWED_SORT = {"numero": "section_checklist.Numero", "titre": "section_checklist.Titre", "checklist_id": "section_checklist.checklist_id", "created_at": "section_checklist.CreatedAt", "updated_at": "section_checklist.UpdatedAt", "id": "section_checklist.Id"}
_ALLOWED_FILTERS = {"checklist_id": "section_checklist.checklist_id"}
_DEFAULT_SORT = "section_checklist.Id"


def count_section_checklists(q: str | None = None, filters: dict[str, Any] | None = None) -> int:
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
        sql = "SELECT COUNT(*) AS total FROM section_checklist WHERE " + " AND ".join(clauses)
    else:
        sql = "SELECT COUNT(*) AS total FROM section_checklist"
    row = fetch_one(sql, params)
    return row["total"] if row else 0


def find_section_checklists_paginated(q: str | None = None, sort: str | None = None, direction: str = "asc", limit: int = 10, offset: int = 0, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    sort_col = _ALLOWED_SORT.get(sort or "", _DEFAULT_SORT)
    sort_dir = "DESC" if direction == "desc" else "ASC"
    base = "SELECT section_checklist.*, checklist.DecisionFinale AS checklist_id_label FROM section_checklist LEFT JOIN checklist ON section_checklist.checklist_id = checklist.Id"
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


def find_section_checklists_for_export(q: str | None = None, sort: str | None = None, direction: str = "asc", filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    return find_section_checklists_paginated(
        q=q, sort=sort, direction=direction,
        limit=_EXPORT_LIMIT, offset=0, filters=filters,
    )



def get_checklist_choices():
    rows = fetch_all("SELECT Id, DecisionFinale FROM checklist ORDER BY DecisionFinale")
    return [(row["Id"], row["DecisionFinale"]) for row in rows]