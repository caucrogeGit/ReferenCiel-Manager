from typing import Any

from core.database.db import fetch_one, fetch_all, execute, insert

SELECT_ALL   = "SELECT progression_eleve.*, eleve.Nom AS eleve_id_label, affectation_parcours.Statut AS affectation_parcours_id_label FROM progression_eleve LEFT JOIN eleve ON progression_eleve.eleve_id = eleve.Id LEFT JOIN affectation_parcours ON progression_eleve.affectation_parcours_id = affectation_parcours.Id ORDER BY progression_eleve.Id"
SELECT_BY_ID = "SELECT progression_eleve.*, eleve.Nom AS eleve_id_label, affectation_parcours.Statut AS affectation_parcours_id_label FROM progression_eleve LEFT JOIN eleve ON progression_eleve.eleve_id = eleve.Id LEFT JOIN affectation_parcours ON progression_eleve.affectation_parcours_id = affectation_parcours.Id WHERE progression_eleve.Id = ?"
INSERT       = "INSERT INTO progression_eleve (Statut, DateDebut, eleve_id, affectation_parcours_id, CreatedAt, UpdatedAt) VALUES (?, ?, ?, ?, ?, ?)"
UPDATE       = "UPDATE progression_eleve SET Statut = ?, DateDebut = ?, eleve_id = ?, affectation_parcours_id = ?, CreatedAt = ?, UpdatedAt = ? WHERE Id = ?"
DELETE       = "DELETE FROM progression_eleve WHERE Id = ?"


def get_progression_eleves():
    return fetch_all(SELECT_ALL)


def get_progression_eleve_by_id(id):
    return fetch_one(SELECT_BY_ID, (id,))


def add_progression_eleve(data):
    return insert(INSERT, (data["statut"], data["date_debut"], data["eleve_id"], data["affectation_parcours_id"], data["created_at"], data["updated_at"],))


def update_progression_eleve(id, data):
    execute(UPDATE, (data["statut"], data["date_debut"], data["eleve_id"], data["affectation_parcours_id"], data["created_at"], data["updated_at"], id))


def delete_progression_eleve(id):
    execute(DELETE, (id,))


def bulk_delete_progression_eleves(ids):
    """Supprime plusieurs enregistrements par ID. Aucune concaténation SQL."""
    if not ids:
        return
    placeholders = ", ".join("?" for _ in ids)
    execute("DELETE FROM progression_eleve WHERE Id IN (" + placeholders + ")", list(ids))


_SEARCH_COLS  = ['progression_eleve.Statut']
_ALLOWED_SORT = {"statut": "progression_eleve.Statut", "date_debut": "progression_eleve.DateDebut", "eleve_id": "progression_eleve.eleve_id", "affectation_parcours_id": "progression_eleve.affectation_parcours_id", "created_at": "progression_eleve.CreatedAt", "updated_at": "progression_eleve.UpdatedAt", "id": "progression_eleve.Id"}
_ALLOWED_FILTERS = {"eleve_id": "progression_eleve.eleve_id", "affectation_parcours_id": "progression_eleve.affectation_parcours_id"}
_DEFAULT_SORT = "progression_eleve.Id"


def count_progression_eleves(q: str | None = None, filters: dict[str, Any] | None = None) -> int:
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
        sql = "SELECT COUNT(*) AS total FROM progression_eleve WHERE " + " AND ".join(clauses)
    else:
        sql = "SELECT COUNT(*) AS total FROM progression_eleve"
    row = fetch_one(sql, params)
    return row["total"] if row else 0


def find_progression_eleves_paginated(q: str | None = None, sort: str | None = None, direction: str = "asc", limit: int = 10, offset: int = 0, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    sort_col = _ALLOWED_SORT.get(sort or "", _DEFAULT_SORT)
    sort_dir = "DESC" if direction == "desc" else "ASC"
    base = "SELECT progression_eleve.*, eleve.Nom AS eleve_id_label, affectation_parcours.Statut AS affectation_parcours_id_label FROM progression_eleve LEFT JOIN eleve ON progression_eleve.eleve_id = eleve.Id LEFT JOIN affectation_parcours ON progression_eleve.affectation_parcours_id = affectation_parcours.Id"
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


def find_progression_eleves_for_export(q: str | None = None, sort: str | None = None, direction: str = "asc", filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    return find_progression_eleves_paginated(
        q=q, sort=sort, direction=direction,
        limit=_EXPORT_LIMIT, offset=0, filters=filters,
    )



def get_eleve_choices():
    rows = fetch_all("SELECT Id, Nom FROM eleve ORDER BY Nom")
    return [(row["Id"], row["Nom"]) for row in rows]


def get_affectation_parcours_choices():
    rows = fetch_all("SELECT Id, Statut FROM affectation_parcours ORDER BY Statut")
    return [(row["Id"], row["Statut"]) for row in rows]