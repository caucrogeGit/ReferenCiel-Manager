from typing import Any

from core.database.db import fetch_one, fetch_all, execute, insert

SELECT_ALL   = "SELECT tentative_qcm.*, progression_palier.Statut AS progression_palier_id_label FROM tentative_qcm LEFT JOIN progression_palier ON tentative_qcm.progression_palier_id = progression_palier.Id ORDER BY tentative_qcm.Id"
SELECT_BY_ID = "SELECT tentative_qcm.*, progression_palier.Statut AS progression_palier_id_label FROM tentative_qcm LEFT JOIN progression_palier ON tentative_qcm.progression_palier_id = progression_palier.Id WHERE tentative_qcm.Id = ?"
INSERT       = "INSERT INTO tentative_qcm (NumeroTentative, Score, Validee, DateTentative, progression_palier_id) VALUES (?, ?, ?, ?, ?)"
UPDATE       = "UPDATE tentative_qcm SET NumeroTentative = ?, Score = ?, Validee = ?, DateTentative = ?, progression_palier_id = ? WHERE Id = ?"
DELETE       = "DELETE FROM tentative_qcm WHERE Id = ?"


def get_tentative_qcms():
    return fetch_all(SELECT_ALL)


def get_tentative_qcm_by_id(id):
    return fetch_one(SELECT_BY_ID, (id,))


def add_tentative_qcm(data):
    return insert(INSERT, (data["numero_tentative"], data["score"], data["validee"], data["date_tentative"], data["progression_palier_id"], ))


def update_tentative_qcm(id, data):
    execute(UPDATE, (data["numero_tentative"], data["score"], data["validee"], data["date_tentative"], data["progression_palier_id"], id))


def delete_tentative_qcm(id):
    execute(DELETE, (id,))


def bulk_delete_tentative_qcms(ids):
    """Supprime plusieurs enregistrements par ID. Aucune concaténation SQL."""
    if not ids:
        return
    placeholders = ", ".join("?" for _ in ids)
    execute("DELETE FROM tentative_qcm WHERE Id IN (" + placeholders + ")", list(ids))


_SEARCH_COLS  = []
_ALLOWED_SORT = {"numero_tentative": "tentative_qcm.NumeroTentative", "score": "tentative_qcm.Score", "validee": "tentative_qcm.Validee", "date_tentative": "tentative_qcm.DateTentative", "progression_palier_id": "tentative_qcm.progression_palier_id", "created_at": "tentative_qcm.CreatedAt", "updated_at": "tentative_qcm.UpdatedAt", "id": "tentative_qcm.Id"}
_ALLOWED_FILTERS = {"progression_palier_id": "tentative_qcm.progression_palier_id"}
_DEFAULT_SORT = "tentative_qcm.Id"


def count_tentative_qcms(q: str | None = None, filters: dict[str, Any] | None = None) -> int:
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
        sql = "SELECT COUNT(*) AS total FROM tentative_qcm WHERE " + " AND ".join(clauses)
    else:
        sql = "SELECT COUNT(*) AS total FROM tentative_qcm"
    row = fetch_one(sql, params)
    return row["total"] if row else 0


def find_tentative_qcms_paginated(q: str | None = None, sort: str | None = None, direction: str = "asc", limit: int = 10, offset: int = 0, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    sort_col = _ALLOWED_SORT.get(sort or "", _DEFAULT_SORT)
    sort_dir = "DESC" if direction == "desc" else "ASC"
    base = "SELECT tentative_qcm.*, progression_palier.Statut AS progression_palier_id_label FROM tentative_qcm LEFT JOIN progression_palier ON tentative_qcm.progression_palier_id = progression_palier.Id"
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


def find_tentative_qcms_for_export(q: str | None = None, sort: str | None = None, direction: str = "asc", filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    return find_tentative_qcms_paginated(
        q=q, sort=sort, direction=direction,
        limit=_EXPORT_LIMIT, offset=0, filters=filters,
    )



def get_progression_palier_choices():
    rows = fetch_all("SELECT Id, Statut FROM progression_palier ORDER BY Statut")
    return [(row["Id"], row["Statut"]) for row in rows]