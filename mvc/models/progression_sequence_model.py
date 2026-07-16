from datetime import datetime, timezone

from typing import Any

from core.database.db import fetch_one, fetch_all, execute, insert

SELECT_ALL   = "SELECT progression_sequence.*, eleve.Nom AS eleve_id_label, sequence.Titre AS sequence_id_label FROM progression_sequence LEFT JOIN eleve ON progression_sequence.eleve_id = eleve.Id LEFT JOIN sequence ON progression_sequence.sequence_id = sequence.Id ORDER BY progression_sequence.Id"
SELECT_BY_ID = "SELECT progression_sequence.*, eleve.Nom AS eleve_id_label, sequence.Titre AS sequence_id_label FROM progression_sequence LEFT JOIN eleve ON progression_sequence.eleve_id = eleve.Id LEFT JOIN sequence ON progression_sequence.sequence_id = sequence.Id WHERE progression_sequence.Id = ?"
INSERT       = "INSERT INTO progression_sequence (Statut, DateDebut, eleve_id, sequence_id, CreatedAt, UpdatedAt) VALUES (?, ?, ?, ?, ?, ?)"
UPDATE       = "UPDATE progression_sequence SET Statut = ?, DateDebut = ?, eleve_id = ?, sequence_id = ?, UpdatedAt = ? WHERE Id = ?"
DELETE       = "DELETE FROM progression_sequence WHERE Id = ?"


def get_progression_sequences():
    return fetch_all(SELECT_ALL)


def get_progression_sequence_by_id(id):
    return fetch_one(SELECT_BY_ID, (id,))


def add_progression_sequence(data):
    return insert(INSERT, (data["statut"], data["date_debut"], data["eleve_id"], data["sequence_id"], datetime.now(timezone.utc), datetime.now(timezone.utc),))


def update_progression_sequence(id, data):
    execute(UPDATE, (data["statut"], data["date_debut"], data["eleve_id"], data["sequence_id"], datetime.now(timezone.utc), id))


def delete_progression_sequence(id):
    execute(DELETE, (id,))


def bulk_delete_progression_sequences(ids):
    """Supprime plusieurs enregistrements par ID. Aucune concaténation SQL."""
    if not ids:
        return
    placeholders = ", ".join("?" for _ in ids)
    execute("DELETE FROM progression_sequence WHERE Id IN (" + placeholders + ")", list(ids))


_SEARCH_COLS  = ['progression_sequence.Statut']
_ALLOWED_SORT = {"statut": "progression_sequence.Statut", "date_debut": "progression_sequence.DateDebut", "eleve_id": "progression_sequence.eleve_id", "sequence_id": "progression_sequence.sequence_id", "id": "progression_sequence.Id"}
_ALLOWED_FILTERS = {"eleve_id": "progression_sequence.eleve_id", "sequence_id": "progression_sequence.sequence_id"}
_DEFAULT_SORT = "progression_sequence.Id"


def count_progression_sequences(q: str | None = None, filters: dict[str, Any] | None = None) -> int:
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
        sql = "SELECT COUNT(*) AS total FROM progression_sequence WHERE " + " AND ".join(clauses)
    else:
        sql = "SELECT COUNT(*) AS total FROM progression_sequence"
    row = fetch_one(sql, params)
    return row["total"] if row else 0


def find_progression_sequences_paginated(q: str | None = None, sort: str | None = None, direction: str = "asc", limit: int = 10, offset: int = 0, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    sort_col = _ALLOWED_SORT.get(sort or "", _DEFAULT_SORT)
    sort_dir = "DESC" if direction == "desc" else "ASC"
    base = "SELECT progression_sequence.*, eleve.Nom AS eleve_id_label, sequence.Titre AS sequence_id_label FROM progression_sequence LEFT JOIN eleve ON progression_sequence.eleve_id = eleve.Id LEFT JOIN sequence ON progression_sequence.sequence_id = sequence.Id"
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


def find_progression_sequences_for_export(q: str | None = None, sort: str | None = None, direction: str = "asc", filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    return find_progression_sequences_paginated(
        q=q, sort=sort, direction=direction,
        limit=_EXPORT_LIMIT, offset=0, filters=filters,
    )



def get_eleve_choices():
    rows = fetch_all("SELECT Id, Nom FROM eleve ORDER BY Nom")
    return [(row["Id"], row["Nom"]) for row in rows]


def get_sequence_choices():
    rows = fetch_all("SELECT Id, Titre FROM sequence ORDER BY Titre")
    return [(row["Id"], row["Titre"]) for row in rows]