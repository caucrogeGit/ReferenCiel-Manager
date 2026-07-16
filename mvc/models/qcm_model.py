from datetime import datetime, timezone

from typing import Any

from core.database.db import fetch_one, fetch_all, execute, insert

SELECT_ALL   = "SELECT qcm.*, dossier_technique.Titre AS dossier_technique_id_label FROM qcm LEFT JOIN dossier_technique ON qcm.dossier_technique_id = dossier_technique.Id ORDER BY qcm.Id"
SELECT_BY_ID = "SELECT qcm.*, dossier_technique.Titre AS dossier_technique_id_label FROM qcm LEFT JOIN dossier_technique ON qcm.dossier_technique_id = dossier_technique.Id WHERE qcm.Id = ?"
INSERT       = "INSERT INTO qcm (FormatReponse, SeuilValidation, dossier_technique_id, CreatedAt, UpdatedAt) VALUES (?, ?, ?, ?, ?)"
UPDATE       = "UPDATE qcm SET FormatReponse = ?, SeuilValidation = ?, dossier_technique_id = ?, UpdatedAt = ? WHERE Id = ?"
DELETE       = "DELETE FROM qcm WHERE Id = ?"


def get_qcms():
    return fetch_all(SELECT_ALL)


def get_qcm_by_id(id):
    return fetch_one(SELECT_BY_ID, (id,))


def add_qcm(data):
    return insert(INSERT, (data["format_reponse"], data["seuil_validation"], data["dossier_technique_id"], datetime.now(timezone.utc), datetime.now(timezone.utc),))


def update_qcm(id, data):
    execute(UPDATE, (data["format_reponse"], data["seuil_validation"], data["dossier_technique_id"], datetime.now(timezone.utc), id))


def delete_qcm(id):
    execute(DELETE, (id,))


def bulk_delete_qcms(ids):
    """Supprime plusieurs enregistrements par ID. Aucune concaténation SQL."""
    if not ids:
        return
    placeholders = ", ".join("?" for _ in ids)
    execute("DELETE FROM qcm WHERE Id IN (" + placeholders + ")", list(ids))


_SEARCH_COLS  = ['qcm.FormatReponse', 'qcm.SeuilValidation']
_ALLOWED_SORT = {"format_reponse": "qcm.FormatReponse", "seuil_validation": "qcm.SeuilValidation", "dossier_technique_id": "qcm.dossier_technique_id", "created_at": "qcm.CreatedAt", "updated_at": "qcm.UpdatedAt", "id": "qcm.Id"}
_ALLOWED_FILTERS = {"dossier_technique_id": "qcm.dossier_technique_id"}
_DEFAULT_SORT = "qcm.Id"


def count_qcms(q: str | None = None, filters: dict[str, Any] | None = None) -> int:
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
        sql = "SELECT COUNT(*) AS total FROM qcm WHERE " + " AND ".join(clauses)
    else:
        sql = "SELECT COUNT(*) AS total FROM qcm"
    row = fetch_one(sql, params)
    return row["total"] if row else 0


def find_qcms_paginated(q: str | None = None, sort: str | None = None, direction: str = "asc", limit: int = 10, offset: int = 0, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    sort_col = _ALLOWED_SORT.get(sort or "", _DEFAULT_SORT)
    sort_dir = "DESC" if direction == "desc" else "ASC"
    base = "SELECT qcm.*, dossier_technique.Titre AS dossier_technique_id_label FROM qcm LEFT JOIN dossier_technique ON qcm.dossier_technique_id = dossier_technique.Id"
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


def find_qcms_for_export(q: str | None = None, sort: str | None = None, direction: str = "asc", filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    return find_qcms_paginated(
        q=q, sort=sort, direction=direction,
        limit=_EXPORT_LIMIT, offset=0, filters=filters,
    )



def get_dossier_technique_choices():
    rows = fetch_all("SELECT Id, Titre FROM dossier_technique ORDER BY Titre")
    return [(row["Id"], row["Titre"]) for row in rows]