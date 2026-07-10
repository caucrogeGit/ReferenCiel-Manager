from typing import Any

from core.database.db import fetch_one, fetch_all, execute, insert

SELECT_ALL   = "SELECT depot_eleve.*, progression_palier.Statut AS progression_palier_id_label, activite.Objectif AS activite_id_label FROM depot_eleve LEFT JOIN progression_palier ON depot_eleve.progression_palier_id = progression_palier.Id LEFT JOIN activite ON depot_eleve.activite_id = activite.Id ORDER BY depot_eleve.Id"
SELECT_BY_ID = "SELECT depot_eleve.*, progression_palier.Statut AS progression_palier_id_label, activite.Objectif AS activite_id_label FROM depot_eleve LEFT JOIN progression_palier ON depot_eleve.progression_palier_id = progression_palier.Id LEFT JOIN activite ON depot_eleve.activite_id = activite.Id WHERE depot_eleve.Id = ?"
INSERT       = "INSERT INTO depot_eleve (Fichier, Commentaire, DateDepot, progression_palier_id, activite_id, CreatedAt, UpdatedAt) VALUES (?, ?, ?, ?, ?, ?, ?)"
UPDATE       = "UPDATE depot_eleve SET Fichier = ?, Commentaire = ?, DateDepot = ?, progression_palier_id = ?, activite_id = ?, CreatedAt = ?, UpdatedAt = ? WHERE Id = ?"
DELETE       = "DELETE FROM depot_eleve WHERE Id = ?"


def get_depot_eleves():
    return fetch_all(SELECT_ALL)


def get_depot_eleve_by_id(id):
    return fetch_one(SELECT_BY_ID, (id,))


def add_depot_eleve(data):
    return insert(INSERT, (data["fichier"], data["commentaire"], data["date_depot"], data["progression_palier_id"], data["activite_id"], data["created_at"], data["updated_at"],))


def update_depot_eleve(id, data):
    execute(UPDATE, (data["fichier"], data["commentaire"], data["date_depot"], data["progression_palier_id"], data["activite_id"], data["created_at"], data["updated_at"], id))


def delete_depot_eleve(id):
    execute(DELETE, (id,))


def bulk_delete_depot_eleves(ids):
    """Supprime plusieurs enregistrements par ID. Aucune concaténation SQL."""
    if not ids:
        return
    placeholders = ", ".join("?" for _ in ids)
    execute("DELETE FROM depot_eleve WHERE Id IN (" + placeholders + ")", list(ids))


_SEARCH_COLS  = ['depot_eleve.Fichier', 'depot_eleve.Commentaire']
_ALLOWED_SORT = {"fichier": "depot_eleve.Fichier", "commentaire": "depot_eleve.Commentaire", "date_depot": "depot_eleve.DateDepot", "progression_palier_id": "depot_eleve.progression_palier_id", "activite_id": "depot_eleve.activite_id", "created_at": "depot_eleve.CreatedAt", "updated_at": "depot_eleve.UpdatedAt", "id": "depot_eleve.Id"}
_ALLOWED_FILTERS = {"progression_palier_id": "depot_eleve.progression_palier_id", "activite_id": "depot_eleve.activite_id"}
_DEFAULT_SORT = "depot_eleve.Id"


def count_depot_eleves(q: str | None = None, filters: dict[str, Any] | None = None) -> int:
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
        sql = "SELECT COUNT(*) AS total FROM depot_eleve WHERE " + " AND ".join(clauses)
    else:
        sql = "SELECT COUNT(*) AS total FROM depot_eleve"
    row = fetch_one(sql, params)
    return row["total"] if row else 0


def find_depot_eleves_paginated(q: str | None = None, sort: str | None = None, direction: str = "asc", limit: int = 10, offset: int = 0, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    sort_col = _ALLOWED_SORT.get(sort or "", _DEFAULT_SORT)
    sort_dir = "DESC" if direction == "desc" else "ASC"
    base = "SELECT depot_eleve.*, progression_palier.Statut AS progression_palier_id_label, activite.Objectif AS activite_id_label FROM depot_eleve LEFT JOIN progression_palier ON depot_eleve.progression_palier_id = progression_palier.Id LEFT JOIN activite ON depot_eleve.activite_id = activite.Id"
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


def find_depot_eleves_for_export(q: str | None = None, sort: str | None = None, direction: str = "asc", filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    return find_depot_eleves_paginated(
        q=q, sort=sort, direction=direction,
        limit=_EXPORT_LIMIT, offset=0, filters=filters,
    )



def get_progression_palier_choices():
    rows = fetch_all("SELECT Id, Statut FROM progression_palier ORDER BY Statut")
    return [(row["Id"], row["Statut"]) for row in rows]


def get_activite_choices():
    rows = fetch_all("SELECT Id, Objectif FROM activite ORDER BY Objectif")
    return [(row["Id"], row["Objectif"]) for row in rows]