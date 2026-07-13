from datetime import datetime, timezone

from typing import Any

from core.database.db import fetch_one, fetch_all, execute, insert

SELECT_ALL   = "SELECT evaluation_critere.*, evaluation_activite.Appreciation AS evaluation_activite_id_label, critere_observable.Libelle AS critere_id_label FROM evaluation_critere LEFT JOIN evaluation_activite ON evaluation_critere.evaluation_activite_id = evaluation_activite.Id LEFT JOIN critere_observable ON evaluation_critere.critere_id = critere_observable.Id ORDER BY evaluation_critere.Id"
SELECT_BY_ID = "SELECT evaluation_critere.*, evaluation_activite.Appreciation AS evaluation_activite_id_label, critere_observable.Libelle AS critere_id_label FROM evaluation_critere LEFT JOIN evaluation_activite ON evaluation_critere.evaluation_activite_id = evaluation_activite.Id LEFT JOIN critere_observable ON evaluation_critere.critere_id = critere_observable.Id WHERE evaluation_critere.Id = ?"
INSERT       = "INSERT INTO evaluation_critere (Niveau, evaluation_activite_id, critere_id, CreatedAt, UpdatedAt) VALUES (?, ?, ?, ?, ?)"
UPDATE       = "UPDATE evaluation_critere SET Niveau = ?, evaluation_activite_id = ?, critere_id = ?, UpdatedAt = ? WHERE Id = ?"
DELETE       = "DELETE FROM evaluation_critere WHERE Id = ?"


def get_evaluation_criteres():
    return fetch_all(SELECT_ALL)


def get_evaluation_critere_by_id(id):
    return fetch_one(SELECT_BY_ID, (id,))


def add_evaluation_critere(data):
    return insert(INSERT, (data["niveau"], data["evaluation_activite_id"], data["critere_id"], datetime.now(timezone.utc), datetime.now(timezone.utc),))


def update_evaluation_critere(id, data):
    execute(UPDATE, (data["niveau"], data["evaluation_activite_id"], data["critere_id"], datetime.now(timezone.utc), id))


def delete_evaluation_critere(id):
    execute(DELETE, (id,))


def bulk_delete_evaluation_criteres(ids):
    """Supprime plusieurs enregistrements par ID. Aucune concaténation SQL."""
    if not ids:
        return
    placeholders = ", ".join("?" for _ in ids)
    execute("DELETE FROM evaluation_critere WHERE Id IN (" + placeholders + ")", list(ids))


_SEARCH_COLS  = ['evaluation_critere.Niveau']
_ALLOWED_SORT = {"niveau": "evaluation_critere.Niveau", "evaluation_activite_id": "evaluation_critere.evaluation_activite_id", "critere_id": "evaluation_critere.critere_id", "created_at": "evaluation_critere.CreatedAt", "updated_at": "evaluation_critere.UpdatedAt", "id": "evaluation_critere.Id"}
_ALLOWED_FILTERS = {"evaluation_activite_id": "evaluation_critere.evaluation_activite_id", "critere_id": "evaluation_critere.critere_id"}
_DEFAULT_SORT = "evaluation_critere.Id"


def count_evaluation_criteres(q: str | None = None, filters: dict[str, Any] | None = None) -> int:
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
        sql = "SELECT COUNT(*) AS total FROM evaluation_critere WHERE " + " AND ".join(clauses)
    else:
        sql = "SELECT COUNT(*) AS total FROM evaluation_critere"
    row = fetch_one(sql, params)
    return row["total"] if row else 0


def find_evaluation_criteres_paginated(q: str | None = None, sort: str | None = None, direction: str = "asc", limit: int = 10, offset: int = 0, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    sort_col = _ALLOWED_SORT.get(sort or "", _DEFAULT_SORT)
    sort_dir = "DESC" if direction == "desc" else "ASC"
    base = "SELECT evaluation_critere.*, evaluation_activite.Appreciation AS evaluation_activite_id_label, critere_observable.Libelle AS critere_id_label FROM evaluation_critere LEFT JOIN evaluation_activite ON evaluation_critere.evaluation_activite_id = evaluation_activite.Id LEFT JOIN critere_observable ON evaluation_critere.critere_id = critere_observable.Id"
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


def find_evaluation_criteres_for_export(q: str | None = None, sort: str | None = None, direction: str = "asc", filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    return find_evaluation_criteres_paginated(
        q=q, sort=sort, direction=direction,
        limit=_EXPORT_LIMIT, offset=0, filters=filters,
    )



def get_evaluation_activite_choices():
    rows = fetch_all("SELECT Id, Appreciation FROM evaluation_activite ORDER BY Appreciation")
    return [(row["Id"], row["Appreciation"]) for row in rows]


def get_critere_observable_choices():
    rows = fetch_all("SELECT Id, Libelle FROM critere_observable ORDER BY Libelle")
    return [(row["Id"], row["Libelle"]) for row in rows]