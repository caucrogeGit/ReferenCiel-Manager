from datetime import datetime, timezone

from typing import Any

from core.database.db import fetch_one, fetch_all, execute, insert

SELECT_ALL   = "SELECT pole_activite.*, referentiel_niveau_classe.Identifiant AS referentiel_id_label FROM pole_activite LEFT JOIN referentiel_niveau_classe ON pole_activite.referentiel_id = referentiel_niveau_classe.Id ORDER BY pole_activite.Id"
SELECT_BY_ID = "SELECT pole_activite.*, referentiel_niveau_classe.Identifiant AS referentiel_id_label FROM pole_activite LEFT JOIN referentiel_niveau_classe ON pole_activite.referentiel_id = referentiel_niveau_classe.Id WHERE pole_activite.Id = ?"
INSERT       = "INSERT INTO pole_activite (Intitule, referentiel_id, CreatedAt, UpdatedAt) VALUES (?, ?, ?, ?)"
UPDATE       = "UPDATE pole_activite SET Intitule = ?, referentiel_id = ?, UpdatedAt = ? WHERE Id = ?"
DELETE       = "DELETE FROM pole_activite WHERE Id = ?"


def get_pole_activites():
    return fetch_all(SELECT_ALL)


def get_pole_activite_by_id(id):
    return fetch_one(SELECT_BY_ID, (id,))


def add_pole_activite(data):
    return insert(INSERT, (data["intitule"], data["referentiel_id"], datetime.now(timezone.utc), datetime.now(timezone.utc),))


def update_pole_activite(id, data):
    execute(UPDATE, (data["intitule"], data["referentiel_id"], datetime.now(timezone.utc), id))


def delete_pole_activite(id):
    execute(DELETE, (id,))


def bulk_delete_pole_activites(ids):
    """Supprime plusieurs enregistrements par ID. Aucune concaténation SQL."""
    if not ids:
        return
    placeholders = ", ".join("?" for _ in ids)
    execute("DELETE FROM pole_activite WHERE Id IN (" + placeholders + ")", list(ids))


_SEARCH_COLS  = ['pole_activite.Intitule']
_ALLOWED_SORT = {"intitule": "pole_activite.Intitule", "referentiel_id": "pole_activite.referentiel_id", "created_at": "pole_activite.CreatedAt", "updated_at": "pole_activite.UpdatedAt", "id": "pole_activite.Id"}
_ALLOWED_FILTERS = {"referentiel_id": "pole_activite.referentiel_id"}
_DEFAULT_SORT = "pole_activite.Id"


def count_pole_activites(q: str | None = None, filters: dict[str, Any] | None = None) -> int:
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
        sql = "SELECT COUNT(*) AS total FROM pole_activite WHERE " + " AND ".join(clauses)
    else:
        sql = "SELECT COUNT(*) AS total FROM pole_activite"
    row = fetch_one(sql, params)
    return row["total"] if row else 0


def find_pole_activites_paginated(q: str | None = None, sort: str | None = None, direction: str = "asc", limit: int = 10, offset: int = 0, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    sort_col = _ALLOWED_SORT.get(sort or "", _DEFAULT_SORT)
    sort_dir = "DESC" if direction == "desc" else "ASC"
    base = "SELECT pole_activite.*, referentiel_niveau_classe.Identifiant AS referentiel_id_label FROM pole_activite LEFT JOIN referentiel_niveau_classe ON pole_activite.referentiel_id = referentiel_niveau_classe.Id"
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


def find_pole_activites_for_export(q: str | None = None, sort: str | None = None, direction: str = "asc", filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    return find_pole_activites_paginated(
        q=q, sort=sort, direction=direction,
        limit=_EXPORT_LIMIT, offset=0, filters=filters,
    )



def get_referentiel_niveau_classe_choices():
    rows = fetch_all("SELECT Id, Identifiant FROM referentiel_niveau_classe ORDER BY Identifiant")
    return [(row["Id"], row["Identifiant"]) for row in rows]