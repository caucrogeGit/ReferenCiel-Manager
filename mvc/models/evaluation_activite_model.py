from typing import Any

from core.database.db import fetch_one, fetch_all, execute, insert

SELECT_ALL   = "SELECT evaluation_activite.*, progression_palier.Statut AS progression_palier_id_label, activite.Objectif AS activite_id_label, professeur.Nom AS professeur_id_label FROM evaluation_activite LEFT JOIN progression_palier ON evaluation_activite.progression_palier_id = progression_palier.Id LEFT JOIN activite ON evaluation_activite.activite_id = activite.Id LEFT JOIN professeur ON evaluation_activite.professeur_id = professeur.Id ORDER BY evaluation_activite.Id"
SELECT_BY_ID = "SELECT evaluation_activite.*, progression_palier.Statut AS progression_palier_id_label, activite.Objectif AS activite_id_label, professeur.Nom AS professeur_id_label FROM evaluation_activite LEFT JOIN progression_palier ON evaluation_activite.progression_palier_id = progression_palier.Id LEFT JOIN activite ON evaluation_activite.activite_id = activite.Id LEFT JOIN professeur ON evaluation_activite.professeur_id = professeur.Id WHERE evaluation_activite.Id = ?"
INSERT       = "INSERT INTO evaluation_activite (DateEvaluation, Appreciation, progression_palier_id, activite_id, professeur_id, CreatedAt, UpdatedAt) VALUES (?, ?, ?, ?, ?, ?, ?)"
UPDATE       = "UPDATE evaluation_activite SET DateEvaluation = ?, Appreciation = ?, progression_palier_id = ?, activite_id = ?, professeur_id = ?, CreatedAt = ?, UpdatedAt = ? WHERE Id = ?"
DELETE       = "DELETE FROM evaluation_activite WHERE Id = ?"


def get_evaluation_activites():
    return fetch_all(SELECT_ALL)


def get_evaluation_activite_by_id(id):
    return fetch_one(SELECT_BY_ID, (id,))


def add_evaluation_activite(data):
    return insert(INSERT, (data["date_evaluation"], data["appreciation"], data["progression_palier_id"], data["activite_id"], data["professeur_id"], data["created_at"], data["updated_at"],))


def update_evaluation_activite(id, data):
    execute(UPDATE, (data["date_evaluation"], data["appreciation"], data["progression_palier_id"], data["activite_id"], data["professeur_id"], data["created_at"], data["updated_at"], id))


def delete_evaluation_activite(id):
    execute(DELETE, (id,))


def bulk_delete_evaluation_activites(ids):
    """Supprime plusieurs enregistrements par ID. Aucune concaténation SQL."""
    if not ids:
        return
    placeholders = ", ".join("?" for _ in ids)
    execute("DELETE FROM evaluation_activite WHERE Id IN (" + placeholders + ")", list(ids))


_SEARCH_COLS  = ['evaluation_activite.Appreciation']
_ALLOWED_SORT = {"date_evaluation": "evaluation_activite.DateEvaluation", "appreciation": "evaluation_activite.Appreciation", "progression_palier_id": "evaluation_activite.progression_palier_id", "activite_id": "evaluation_activite.activite_id", "professeur_id": "evaluation_activite.professeur_id", "created_at": "evaluation_activite.CreatedAt", "updated_at": "evaluation_activite.UpdatedAt", "id": "evaluation_activite.Id"}
_ALLOWED_FILTERS = {"progression_palier_id": "evaluation_activite.progression_palier_id", "activite_id": "evaluation_activite.activite_id", "professeur_id": "evaluation_activite.professeur_id"}
_DEFAULT_SORT = "evaluation_activite.Id"


def count_evaluation_activites(q: str | None = None, filters: dict[str, Any] | None = None) -> int:
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
        sql = "SELECT COUNT(*) AS total FROM evaluation_activite WHERE " + " AND ".join(clauses)
    else:
        sql = "SELECT COUNT(*) AS total FROM evaluation_activite"
    row = fetch_one(sql, params)
    return row["total"] if row else 0


def find_evaluation_activites_paginated(q: str | None = None, sort: str | None = None, direction: str = "asc", limit: int = 10, offset: int = 0, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    sort_col = _ALLOWED_SORT.get(sort or "", _DEFAULT_SORT)
    sort_dir = "DESC" if direction == "desc" else "ASC"
    base = "SELECT evaluation_activite.*, progression_palier.Statut AS progression_palier_id_label, activite.Objectif AS activite_id_label, professeur.Nom AS professeur_id_label FROM evaluation_activite LEFT JOIN progression_palier ON evaluation_activite.progression_palier_id = progression_palier.Id LEFT JOIN activite ON evaluation_activite.activite_id = activite.Id LEFT JOIN professeur ON evaluation_activite.professeur_id = professeur.Id"
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


def find_evaluation_activites_for_export(q: str | None = None, sort: str | None = None, direction: str = "asc", filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    return find_evaluation_activites_paginated(
        q=q, sort=sort, direction=direction,
        limit=_EXPORT_LIMIT, offset=0, filters=filters,
    )



def get_progression_palier_choices():
    rows = fetch_all("SELECT Id, Statut FROM progression_palier ORDER BY Statut")
    return [(row["Id"], row["Statut"]) for row in rows]


def get_activite_choices():
    rows = fetch_all("SELECT Id, Objectif FROM activite ORDER BY Objectif")
    return [(row["Id"], row["Objectif"]) for row in rows]


def get_professeur_choices():
    rows = fetch_all("SELECT Id, Nom FROM professeur ORDER BY Nom")
    return [(row["Id"], row["Nom"]) for row in rows]