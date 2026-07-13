from datetime import datetime, timezone

from typing import Any

from core.database.db import fetch_one, fetch_all, execute, insert

SELECT_ALL   = "SELECT competence.*, referentiel_niveau_classe.Identifiant AS referentiel_id_label FROM competence LEFT JOIN referentiel_niveau_classe ON competence.referentiel_id = referentiel_niveau_classe.Id ORDER BY competence.Id"
SELECT_BY_ID = "SELECT competence.*, referentiel_niveau_classe.Identifiant AS referentiel_id_label FROM competence LEFT JOIN referentiel_niveau_classe ON competence.referentiel_id = referentiel_niveau_classe.Id WHERE competence.Id = ?"
INSERT       = "INSERT INTO competence (Code, Intitule, referentiel_id, CreatedAt, UpdatedAt) VALUES (?, ?, ?, ?, ?)"
UPDATE       = "UPDATE competence SET Code = ?, Intitule = ?, referentiel_id = ?, UpdatedAt = ? WHERE Id = ?"
DELETE       = "DELETE FROM competence WHERE Id = ?"


def get_competences():
    return fetch_all(SELECT_ALL)


def get_competence_by_id(id):
    return fetch_one(SELECT_BY_ID, (id,))


def add_competence(data):
    return insert(INSERT, (data["code"], data["intitule"], data["referentiel_id"], datetime.now(timezone.utc), datetime.now(timezone.utc),))


def update_competence(id, data):
    execute(UPDATE, (data["code"], data["intitule"], data["referentiel_id"], datetime.now(timezone.utc), id))


def delete_competence(id):
    execute(DELETE, (id,))


def bulk_delete_competences(ids):
    """Supprime plusieurs enregistrements par ID. Aucune concaténation SQL."""
    if not ids:
        return
    placeholders = ", ".join("?" for _ in ids)
    execute("DELETE FROM competence WHERE Id IN (" + placeholders + ")", list(ids))


_SEARCH_COLS  = ['competence.Code', 'competence.Intitule']
_ALLOWED_SORT = {"code": "competence.Code", "intitule": "competence.Intitule", "referentiel_id": "competence.referentiel_id", "created_at": "competence.CreatedAt", "updated_at": "competence.UpdatedAt", "id": "competence.Id"}
_ALLOWED_FILTERS = {"referentiel_id": "competence.referentiel_id"}
_DEFAULT_SORT = "competence.Id"


def count_competences(q: str | None = None, filters: dict[str, Any] | None = None) -> int:
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
        sql = "SELECT COUNT(*) AS total FROM competence WHERE " + " AND ".join(clauses)
    else:
        sql = "SELECT COUNT(*) AS total FROM competence"
    row = fetch_one(sql, params)
    return row["total"] if row else 0


def find_competences_paginated(q: str | None = None, sort: str | None = None, direction: str = "asc", limit: int = 10, offset: int = 0, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    sort_col = _ALLOWED_SORT.get(sort or "", _DEFAULT_SORT)
    sort_dir = "DESC" if direction == "desc" else "ASC"
    base = "SELECT competence.*, referentiel_niveau_classe.Identifiant AS referentiel_id_label FROM competence LEFT JOIN referentiel_niveau_classe ON competence.referentiel_id = referentiel_niveau_classe.Id"
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


def find_competences_for_export(q: str | None = None, sort: str | None = None, direction: str = "asc", filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    return find_competences_paginated(
        q=q, sort=sort, direction=direction,
        limit=_EXPORT_LIMIT, offset=0, filters=filters,
    )



def get_referentiel_niveau_classe_choices():
    rows = fetch_all("SELECT Id, Identifiant FROM referentiel_niveau_classe ORDER BY Identifiant")
    return [(row["Id"], row["Identifiant"]) for row in rows]