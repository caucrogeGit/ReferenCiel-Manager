from typing import Any

from core.database.db import fetch_one, fetch_all, execute, insert

SELECT_ALL   = "SELECT critere_observable.*, competence.Code AS competence_id_label FROM critere_observable LEFT JOIN competence ON critere_observable.competence_id = competence.Id ORDER BY critere_observable.Id"
SELECT_BY_ID = "SELECT critere_observable.*, competence.Code AS competence_id_label FROM critere_observable LEFT JOIN competence ON critere_observable.competence_id = competence.Id WHERE critere_observable.Id = ?"
INSERT       = "INSERT INTO critere_observable (Code, Libelle, competence_id) VALUES (?, ?, ?)"
UPDATE       = "UPDATE critere_observable SET Code = ?, Libelle = ?, competence_id = ? WHERE Id = ?"
DELETE       = "DELETE FROM critere_observable WHERE Id = ?"


def get_critere_observables():
    return fetch_all(SELECT_ALL)


def get_critere_observable_by_id(id):
    return fetch_one(SELECT_BY_ID, (id,))


def add_critere_observable(data):
    return insert(INSERT, (data["code"], data["libelle"], data["competence_id"], ))


def update_critere_observable(id, data):
    execute(UPDATE, (data["code"], data["libelle"], data["competence_id"], id))


def delete_critere_observable(id):
    execute(DELETE, (id,))


def bulk_delete_critere_observables(ids):
    """Supprime plusieurs enregistrements par ID. Aucune concaténation SQL."""
    if not ids:
        return
    placeholders = ", ".join("?" for _ in ids)
    execute("DELETE FROM critere_observable WHERE Id IN (" + placeholders + ")", list(ids))


_SEARCH_COLS  = ['critere_observable.Code', 'critere_observable.Libelle']
_ALLOWED_SORT = {"code": "critere_observable.Code", "libelle": "critere_observable.Libelle", "competence_id": "critere_observable.competence_id", "created_at": "critere_observable.CreatedAt", "updated_at": "critere_observable.UpdatedAt", "id": "critere_observable.Id"}
_ALLOWED_FILTERS = {"competence_id": "critere_observable.competence_id"}
_DEFAULT_SORT = "critere_observable.Id"


def count_critere_observables(q: str | None = None, filters: dict[str, Any] | None = None) -> int:
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
        sql = "SELECT COUNT(*) AS total FROM critere_observable WHERE " + " AND ".join(clauses)
    else:
        sql = "SELECT COUNT(*) AS total FROM critere_observable"
    row = fetch_one(sql, params)
    return row["total"] if row else 0


def find_critere_observables_paginated(q: str | None = None, sort: str | None = None, direction: str = "asc", limit: int = 10, offset: int = 0, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    sort_col = _ALLOWED_SORT.get(sort or "", _DEFAULT_SORT)
    sort_dir = "DESC" if direction == "desc" else "ASC"
    base = "SELECT critere_observable.*, competence.Code AS competence_id_label FROM critere_observable LEFT JOIN competence ON critere_observable.competence_id = competence.Id"
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


def find_critere_observables_for_export(q: str | None = None, sort: str | None = None, direction: str = "asc", filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    return find_critere_observables_paginated(
        q=q, sort=sort, direction=direction,
        limit=_EXPORT_LIMIT, offset=0, filters=filters,
    )



def get_competence_choices():
    rows = fetch_all("SELECT Id, Code FROM competence ORDER BY Code")
    return [(row["Id"], row["Code"]) for row in rows]