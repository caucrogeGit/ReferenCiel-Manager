from typing import Any

from core.database.db import fetch_one, fetch_all, execute, insert

SELECT_ALL   = "SELECT reponse_qcm.*, tentative_qcm.Id AS tentative_id_label, question_qcm.Enonce AS question_id_label, choix_qcm.Lettre AS choix_id_label FROM reponse_qcm LEFT JOIN tentative_qcm ON reponse_qcm.tentative_id = tentative_qcm.Id LEFT JOIN question_qcm ON reponse_qcm.question_id = question_qcm.Id LEFT JOIN choix_qcm ON reponse_qcm.choix_id = choix_qcm.Id ORDER BY reponse_qcm.Id"
SELECT_BY_ID = "SELECT reponse_qcm.*, tentative_qcm.Id AS tentative_id_label, question_qcm.Enonce AS question_id_label, choix_qcm.Lettre AS choix_id_label FROM reponse_qcm LEFT JOIN tentative_qcm ON reponse_qcm.tentative_id = tentative_qcm.Id LEFT JOIN question_qcm ON reponse_qcm.question_id = question_qcm.Id LEFT JOIN choix_qcm ON reponse_qcm.choix_id = choix_qcm.Id WHERE reponse_qcm.Id = ?"
INSERT       = "INSERT INTO reponse_qcm (EstCorrecte, tentative_id, question_id, choix_id) VALUES (?, ?, ?, ?)"
UPDATE       = "UPDATE reponse_qcm SET EstCorrecte = ?, tentative_id = ?, question_id = ?, choix_id = ? WHERE Id = ?"
DELETE       = "DELETE FROM reponse_qcm WHERE Id = ?"


def get_reponse_qcms():
    return fetch_all(SELECT_ALL)


def get_reponse_qcm_by_id(id):
    return fetch_one(SELECT_BY_ID, (id,))


def add_reponse_qcm(data):
    return insert(INSERT, (data["est_correcte"], data["tentative_id"], data["question_id"], data["choix_id"], ))


def update_reponse_qcm(id, data):
    execute(UPDATE, (data["est_correcte"], data["tentative_id"], data["question_id"], data["choix_id"], id))


def delete_reponse_qcm(id):
    execute(DELETE, (id,))


def bulk_delete_reponse_qcms(ids):
    """Supprime plusieurs enregistrements par ID. Aucune concaténation SQL."""
    if not ids:
        return
    placeholders = ", ".join("?" for _ in ids)
    execute("DELETE FROM reponse_qcm WHERE Id IN (" + placeholders + ")", list(ids))


_SEARCH_COLS  = []
_ALLOWED_SORT = {"est_correcte": "reponse_qcm.EstCorrecte", "tentative_id": "reponse_qcm.tentative_id", "question_id": "reponse_qcm.question_id", "choix_id": "reponse_qcm.choix_id", "created_at": "reponse_qcm.CreatedAt", "updated_at": "reponse_qcm.UpdatedAt", "id": "reponse_qcm.Id"}
_ALLOWED_FILTERS = {"tentative_id": "reponse_qcm.tentative_id", "question_id": "reponse_qcm.question_id", "choix_id": "reponse_qcm.choix_id"}
_DEFAULT_SORT = "reponse_qcm.Id"


def count_reponse_qcms(q: str | None = None, filters: dict[str, Any] | None = None) -> int:
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
        sql = "SELECT COUNT(*) AS total FROM reponse_qcm WHERE " + " AND ".join(clauses)
    else:
        sql = "SELECT COUNT(*) AS total FROM reponse_qcm"
    row = fetch_one(sql, params)
    return row["total"] if row else 0


def find_reponse_qcms_paginated(q: str | None = None, sort: str | None = None, direction: str = "asc", limit: int = 10, offset: int = 0, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    sort_col = _ALLOWED_SORT.get(sort or "", _DEFAULT_SORT)
    sort_dir = "DESC" if direction == "desc" else "ASC"
    base = "SELECT reponse_qcm.*, tentative_qcm.Id AS tentative_id_label, question_qcm.Enonce AS question_id_label, choix_qcm.Lettre AS choix_id_label FROM reponse_qcm LEFT JOIN tentative_qcm ON reponse_qcm.tentative_id = tentative_qcm.Id LEFT JOIN question_qcm ON reponse_qcm.question_id = question_qcm.Id LEFT JOIN choix_qcm ON reponse_qcm.choix_id = choix_qcm.Id"
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


def find_reponse_qcms_for_export(q: str | None = None, sort: str | None = None, direction: str = "asc", filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    return find_reponse_qcms_paginated(
        q=q, sort=sort, direction=direction,
        limit=_EXPORT_LIMIT, offset=0, filters=filters,
    )



def get_tentative_qcm_choices():
    rows = fetch_all("SELECT Id FROM tentative_qcm ORDER BY Id")
    return [(row["Id"], row["Id"]) for row in rows]


def get_question_qcm_choices():
    rows = fetch_all("SELECT Id, Enonce FROM question_qcm ORDER BY Enonce")
    return [(row["Id"], row["Enonce"]) for row in rows]


def get_choix_qcm_choices():
    rows = fetch_all("SELECT Id, Lettre FROM choix_qcm ORDER BY Lettre")
    return [(row["Id"], row["Lettre"]) for row in rows]