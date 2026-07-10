from typing import Any

from core.database.db import fetch_one, fetch_all, execute, insert

SELECT_ALL   = "SELECT question_qcm.*, qcm.FormatReponse AS qcm_id_label FROM question_qcm LEFT JOIN qcm ON question_qcm.qcm_id = qcm.Id ORDER BY question_qcm.Id"
SELECT_BY_ID = "SELECT question_qcm.*, qcm.FormatReponse AS qcm_id_label FROM question_qcm LEFT JOIN qcm ON question_qcm.qcm_id = qcm.Id WHERE question_qcm.Id = ?"
INSERT       = "INSERT INTO question_qcm (Numero, Enonce, BonneReponse, qcm_id, CreatedAt, UpdatedAt) VALUES (?, ?, ?, ?, ?, ?)"
UPDATE       = "UPDATE question_qcm SET Numero = ?, Enonce = ?, BonneReponse = ?, qcm_id = ?, CreatedAt = ?, UpdatedAt = ? WHERE Id = ?"
DELETE       = "DELETE FROM question_qcm WHERE Id = ?"


def get_question_qcms():
    return fetch_all(SELECT_ALL)


def get_question_qcm_by_id(id):
    return fetch_one(SELECT_BY_ID, (id,))


def add_question_qcm(data):
    return insert(INSERT, (data["numero"], data["enonce"], data["bonne_reponse"], data["qcm_id"], data["created_at"], data["updated_at"],))


def update_question_qcm(id, data):
    execute(UPDATE, (data["numero"], data["enonce"], data["bonne_reponse"], data["qcm_id"], data["created_at"], data["updated_at"], id))


def delete_question_qcm(id):
    execute(DELETE, (id,))


def bulk_delete_question_qcms(ids):
    """Supprime plusieurs enregistrements par ID. Aucune concaténation SQL."""
    if not ids:
        return
    placeholders = ", ".join("?" for _ in ids)
    execute("DELETE FROM question_qcm WHERE Id IN (" + placeholders + ")", list(ids))


_SEARCH_COLS  = ['question_qcm.Enonce', 'question_qcm.BonneReponse']
_ALLOWED_SORT = {"numero": "question_qcm.Numero", "enonce": "question_qcm.Enonce", "bonne_reponse": "question_qcm.BonneReponse", "qcm_id": "question_qcm.qcm_id", "created_at": "question_qcm.CreatedAt", "updated_at": "question_qcm.UpdatedAt", "id": "question_qcm.Id"}
_ALLOWED_FILTERS = {"qcm_id": "question_qcm.qcm_id"}
_DEFAULT_SORT = "question_qcm.Id"


def count_question_qcms(q: str | None = None, filters: dict[str, Any] | None = None) -> int:
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
        sql = "SELECT COUNT(*) AS total FROM question_qcm WHERE " + " AND ".join(clauses)
    else:
        sql = "SELECT COUNT(*) AS total FROM question_qcm"
    row = fetch_one(sql, params)
    return row["total"] if row else 0


def find_question_qcms_paginated(q: str | None = None, sort: str | None = None, direction: str = "asc", limit: int = 10, offset: int = 0, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    sort_col = _ALLOWED_SORT.get(sort or "", _DEFAULT_SORT)
    sort_dir = "DESC" if direction == "desc" else "ASC"
    base = "SELECT question_qcm.*, qcm.FormatReponse AS qcm_id_label FROM question_qcm LEFT JOIN qcm ON question_qcm.qcm_id = qcm.Id"
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


def find_question_qcms_for_export(q: str | None = None, sort: str | None = None, direction: str = "asc", filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    return find_question_qcms_paginated(
        q=q, sort=sort, direction=direction,
        limit=_EXPORT_LIMIT, offset=0, filters=filters,
    )



def get_qcm_choices():
    rows = fetch_all("SELECT Id, FormatReponse FROM qcm ORDER BY FormatReponse")
    return [(row["Id"], row["FormatReponse"]) for row in rows]