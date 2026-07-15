from datetime import datetime, timezone

from typing import Any

from core.database.db import fetch_one, fetch_all, execute, insert

# Lectures : jointure vers classe pour exposer un libellé (classe_id_label).
_SELECT_BASE = (
    "SELECT eleve.*, classe.Code AS classe_id_label "
    "FROM eleve "
    "LEFT JOIN classe ON eleve.classe_id = classe.Id"
)
SELECT_ALL   = _SELECT_BASE + " ORDER BY eleve.Id"
SELECT_BY_ID = _SELECT_BASE + " WHERE eleve.Id = ?"
INSERT       = "INSERT INTO eleve (Nom, Prenom, Identifiant, DateNaissance, UserId, classe_id, CreatedAt, UpdatedAt) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
UPDATE       = "UPDATE eleve SET Nom = ?, Prenom = ?, Identifiant = ?, DateNaissance = ?, UserId = ?, classe_id = ?, UpdatedAt = ? WHERE Id = ?"
DELETE       = "DELETE FROM eleve WHERE Id = ?"


def get_classe_choices() -> list[tuple[Any, str]]:
    """Options (Id, libellé) pour le champ « Niveau de classe » du formulaire."""
    rows = fetch_all("SELECT Id, Code, Libelle FROM classe ORDER BY Code")
    return [(row["Id"], f"{row['Code']} — {row['Libelle']}") for row in rows]


def get_eleves():
    return fetch_all(SELECT_ALL)


def get_eleve_by_id(id):
    return fetch_one(SELECT_BY_ID, (id,))


def add_eleve(data):
    return insert(INSERT, (data["nom"], data["prenom"], data["identifiant"], data["date_naissance"], data["user_id"], data["classe_id"], datetime.now(timezone.utc), datetime.now(timezone.utc),))


def update_eleve(id, data):
    execute(UPDATE, (data["nom"], data["prenom"], data["identifiant"], data["date_naissance"], data["user_id"], data["classe_id"], datetime.now(timezone.utc), id))


def delete_eleve(id):
    execute(DELETE, (id,))


def bulk_delete_eleves(ids):
    """Supprime plusieurs enregistrements par ID. Aucune concaténation SQL."""
    if not ids:
        return
    placeholders = ", ".join("?" for _ in ids)
    execute("DELETE FROM eleve WHERE Id IN (" + placeholders + ")", list(ids))


_SEARCH_COLS  = ['Nom', 'Prenom', 'Identifiant']
_ALLOWED_SORT = {"nom": "Nom", "prenom": "Prenom", "identifiant": "Identifiant", "date_naissance": "DateNaissance", "user_id": "UserId", "classe_id": "eleve.classe_id", "created_at": "CreatedAt", "updated_at": "UpdatedAt", "id": "eleve.Id"}
_ALLOWED_FILTERS = {}
_DEFAULT_SORT = "eleve.Id"


def count_eleves(q: str | None = None, filters: dict[str, Any] | None = None) -> int:
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
        sql = "SELECT COUNT(*) AS total FROM eleve WHERE " + " AND ".join(clauses)
    else:
        sql = "SELECT COUNT(*) AS total FROM eleve"
    row = fetch_one(sql, params)
    return row["total"] if row else 0


def find_eleves_paginated(q: str | None = None, sort: str | None = None, direction: str = "asc", limit: int = 10, offset: int = 0, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    sort_col = _ALLOWED_SORT.get(sort or "", _DEFAULT_SORT)
    sort_dir = "DESC" if direction == "desc" else "ASC"
    base = _SELECT_BASE
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


def find_eleves_for_export(q: str | None = None, sort: str | None = None, direction: str = "asc", filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    return find_eleves_paginated(
        q=q, sort=sort, direction=direction,
        limit=_EXPORT_LIMIT, offset=0, filters=filters,
    )
