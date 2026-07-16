from datetime import datetime, timezone

from typing import Any

from core.database.db import fetch_one, fetch_all, execute, insert

SELECT_ALL   = "SELECT seance.*, parcours.Titre AS parcours_id_label FROM seance LEFT JOIN parcours ON seance.parcours_id = parcours.Id ORDER BY seance.Id"
SELECT_BY_ID = "SELECT seance.*, parcours.Titre AS parcours_id_label FROM seance LEFT JOIN parcours ON seance.parcours_id = parcours.Id WHERE seance.Id = ?"
INSERT       = "INSERT INTO seance (Ordre, Titre, Theme, ProductionAttendue, parcours_id, CreatedAt, UpdatedAt) VALUES (?, ?, ?, ?, ?, ?, ?)"
UPDATE       = "UPDATE seance SET Ordre = ?, Titre = ?, Theme = ?, ProductionAttendue = ?, parcours_id = ?, UpdatedAt = ? WHERE Id = ?"
DELETE       = "DELETE FROM seance WHERE Id = ?"


def get_seances():
    return fetch_all(SELECT_ALL)


def get_seance_by_id(id):
    return fetch_one(SELECT_BY_ID, (id,))


def add_seance(data):
    return insert(INSERT, (data["ordre"], data["titre"], data["theme"], data["production_attendue"], data["parcours_id"], datetime.now(timezone.utc), datetime.now(timezone.utc),))


def update_seance(id, data):
    execute(UPDATE, (data["ordre"], data["titre"], data["theme"], data["production_attendue"], data["parcours_id"], datetime.now(timezone.utc), id))


def delete_seance(id):
    execute(DELETE, (id,))


def bulk_delete_seances(ids):
    """Supprime plusieurs enregistrements par ID. Aucune concaténation SQL."""
    if not ids:
        return
    placeholders = ", ".join("?" for _ in ids)
    execute("DELETE FROM seance WHERE Id IN (" + placeholders + ")", list(ids))


_SEARCH_COLS  = ['seance.Titre', 'seance.Theme', 'seance.ProductionAttendue']
_ALLOWED_SORT = {"ordre": "seance.Ordre", "titre": "seance.Titre", "theme": "seance.Theme", "production_attendue": "seance.ProductionAttendue", "parcours_id": "seance.parcours_id", "id": "seance.Id"}
_ALLOWED_FILTERS = {"parcours_id": "seance.parcours_id"}
_DEFAULT_SORT = "seance.Id"


def count_seances(q: str | None = None, filters: dict[str, Any] | None = None) -> int:
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
        sql = "SELECT COUNT(*) AS total FROM seance WHERE " + " AND ".join(clauses)
    else:
        sql = "SELECT COUNT(*) AS total FROM seance"
    row = fetch_one(sql, params)
    return row["total"] if row else 0


def find_seances_paginated(q: str | None = None, sort: str | None = None, direction: str = "asc", limit: int = 10, offset: int = 0, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    sort_col = _ALLOWED_SORT.get(sort or "", _DEFAULT_SORT)
    sort_dir = "DESC" if direction == "desc" else "ASC"
    base = "SELECT seance.*, parcours.Titre AS parcours_id_label FROM seance LEFT JOIN parcours ON seance.parcours_id = parcours.Id"
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


def find_seances_for_export(q: str | None = None, sort: str | None = None, direction: str = "asc", filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    return find_seances_paginated(
        q=q, sort=sort, direction=direction,
        limit=_EXPORT_LIMIT, offset=0, filters=filters,
    )



def get_parcours_choices():
    rows = fetch_all("SELECT Id, Titre FROM parcours ORDER BY Titre")
    return [(row["Id"], row["Titre"]) for row in rows]