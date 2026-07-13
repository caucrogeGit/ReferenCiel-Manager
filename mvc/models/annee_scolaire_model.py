# pyright: strict
"""Modèle d'accès aux données de l'entité AnneeScolaire (SQL explicite, Forge).

Généré par `forge make:crud`, puis typé strict (standard du projet, ADR-007).
Toutes les requêtes sont paramétrées (`?`) — jamais d'interpolation.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from core.database.db import execute, fetch_all, fetch_one, insert

SELECT_ALL = "SELECT * FROM annee_scolaire ORDER BY Id"
SELECT_BY_ID = "SELECT * FROM annee_scolaire WHERE Id = ?"
INSERT = "INSERT INTO annee_scolaire (Libelle, DateDebut, DateFin, Active) VALUES (?, ?, ?, ?)"
UPDATE = "UPDATE annee_scolaire SET Libelle = ?, DateDebut = ?, DateFin = ?, Active = ? WHERE Id = ?"
DELETE = "DELETE FROM annee_scolaire WHERE Id = ?"


def get_annee_scolaires() -> list[dict[str, Any]]:
    return fetch_all(SELECT_ALL)


def get_annee_scolaire_by_id(id: int) -> dict[str, Any] | None:
    return fetch_one(SELECT_BY_ID, (id,))


def add_annee_scolaire(data: dict[str, Any]) -> int:
    return insert(
        INSERT,
        (data["libelle"], data["date_debut"], data["date_fin"], data["active"]),
    )


def update_annee_scolaire(id: int, data: dict[str, Any]) -> None:
    execute(
        UPDATE,
        (data["libelle"], data["date_debut"], data["date_fin"], data["active"], id),
    )


def delete_annee_scolaire(id: int) -> None:
    execute(DELETE, (id,))


def bulk_delete_annee_scolaires(ids: Sequence[Any]) -> None:
    """Supprime plusieurs enregistrements par ID. Aucune concaténation SQL."""
    if not ids:
        return
    placeholders = ", ".join("?" for _ in ids)
    execute("DELETE FROM annee_scolaire WHERE Id IN (" + placeholders + ")", list(ids))


_SEARCH_COLS: list[str] = ["Libelle"]
_ALLOWED_SORT: dict[str, str] = {
    "libelle": "Libelle", "date_debut": "DateDebut", "date_fin": "DateFin",
    "active": "Active", "created_at": "CreatedAt", "updated_at": "UpdatedAt", "id": "Id",
}
_ALLOWED_FILTERS: dict[str, str] = {}
_DEFAULT_SORT = "Id"


def count_annee_scolaires(q: str | None = None, filters: dict[str, Any] | None = None) -> int:
    clauses: list[str] = []
    params: list[Any] = []
    if q and _SEARCH_COLS:
        clauses.append("(" + " OR ".join(c + " LIKE ?" for c in _SEARCH_COLS) + ")")
        params.extend("%" + q + "%" for _ in _SEARCH_COLS)
    used_filters: dict[str, Any] = filters or {}
    for key, val in used_filters.items():
        if val is not None and val != "":
            col = _ALLOWED_FILTERS.get(key)
            if col is None:
                raise ValueError(f"Filtre interdit : {key}")
            clauses.append(col + " = ?")
            params.append(val)
    if clauses:
        sql = "SELECT COUNT(*) AS total FROM annee_scolaire WHERE " + " AND ".join(clauses)
    else:
        sql = "SELECT COUNT(*) AS total FROM annee_scolaire"
    row = fetch_one(sql, params)
    return int(row["total"]) if row else 0


def find_annee_scolaires_paginated(
    q: str | None = None,
    sort: str | None = None,
    direction: str = "asc",
    limit: int = 10,
    offset: int = 0,
    filters: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    sort_col = _ALLOWED_SORT.get(sort or "", _DEFAULT_SORT)
    sort_dir = "DESC" if direction == "desc" else "ASC"
    base = "SELECT * FROM annee_scolaire"
    clauses: list[str] = []
    params: list[Any] = []
    if q and _SEARCH_COLS:
        clauses.append("(" + " OR ".join(c + " LIKE ?" for c in _SEARCH_COLS) + ")")
        params.extend("%" + q + "%" for _ in _SEARCH_COLS)
    used_filters: dict[str, Any] = filters or {}
    for key, val in used_filters.items():
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


def find_annee_scolaires_for_export(
    q: str | None = None,
    sort: str | None = None,
    direction: str = "asc",
    filters: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    return find_annee_scolaires_paginated(
        q=q, sort=sort, direction=direction, limit=_EXPORT_LIMIT, offset=0, filters=filters,
    )
