from typing import Any

from core.database.db import fetch_one, fetch_all, execute, insert

SELECT_ALL   = "SELECT choix_qcm.*, question_qcm.Enonce AS question_id_label FROM choix_qcm LEFT JOIN question_qcm ON choix_qcm.question_id = question_qcm.Id ORDER BY choix_qcm.Id"
SELECT_BY_ID = "SELECT choix_qcm.*, question_qcm.Enonce AS question_id_label FROM choix_qcm LEFT JOIN question_qcm ON choix_qcm.question_id = question_qcm.Id WHERE choix_qcm.Id = ?"
INSERT       = "INSERT INTO choix_qcm (Lettre, Texte, question_id) VALUES (?, ?, ?)"
UPDATE       = "UPDATE choix_qcm SET Lettre = ?, Texte = ?, question_id = ? WHERE Id = ?"
DELETE       = "DELETE FROM choix_qcm WHERE Id = ?"


def get_choix_qcms():
    return fetch_all(SELECT_ALL)


def get_choix_qcm_by_id(id):
    return fetch_one(SELECT_BY_ID, (id,))


def add_choix_qcm(data):
    return insert(INSERT, (data["lettre"], data["texte"], data["question_id"], ))


def update_choix_qcm(id, data):
    execute(UPDATE, (data["lettre"], data["texte"], data["question_id"], id))


def delete_choix_qcm(id):
    execute(DELETE, (id,))


def bulk_delete_choix_qcms(ids):
    """Supprime plusieurs enregistrements par ID. Aucune concaténation SQL."""
    if not ids:
        return
    placeholders = ", ".join("?" for _ in ids)
    execute("DELETE FROM choix_qcm WHERE Id IN (" + placeholders + ")", list(ids))


_SEARCH_COLS  = ['choix_qcm.Lettre', 'choix_qcm.Texte']
_ALLOWED_SORT = {"lettre": "choix_qcm.Lettre", "texte": "choix_qcm.Texte", "question_id": "choix_qcm.question_id", "created_at": "choix_qcm.CreatedAt", "updated_at": "choix_qcm.UpdatedAt", "id": "choix_qcm.Id"}
_ALLOWED_FILTERS = {"question_id": "choix_qcm.question_id"}
_DEFAULT_SORT = "choix_qcm.Id"


def count_choix_qcms(q: str | None = None, filters: dict[str, Any] | None = None) -> int:
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
        sql = "SELECT COUNT(*) AS total FROM choix_qcm WHERE " + " AND ".join(clauses)
    else:
        sql = "SELECT COUNT(*) AS total FROM choix_qcm"
    row = fetch_one(sql, params)
    return row["total"] if row else 0


def find_choix_qcms_paginated(q: str | None = None, sort: str | None = None, direction: str = "asc", limit: int = 10, offset: int = 0, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    sort_col = _ALLOWED_SORT.get(sort or "", _DEFAULT_SORT)
    sort_dir = "DESC" if direction == "desc" else "ASC"
    base = "SELECT choix_qcm.*, question_qcm.Enonce AS question_id_label FROM choix_qcm LEFT JOIN question_qcm ON choix_qcm.question_id = question_qcm.Id"
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


def find_choix_qcms_for_export(q: str | None = None, sort: str | None = None, direction: str = "asc", filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    return find_choix_qcms_paginated(
        q=q, sort=sort, direction=direction,
        limit=_EXPORT_LIMIT, offset=0, filters=filters,
    )



def get_question_qcm_choices():
    rows = fetch_all("SELECT Id, Enonce FROM question_qcm ORDER BY Enonce")
    return [(row["Id"], row["Enonce"]) for row in rows]