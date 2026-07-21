from datetime import datetime, timezone

from typing import Any

from core.database.db import fetch_one, fetch_all, execute, insert

SELECT_ALL   = "SELECT formation_niveau.*, formation.Code AS formation_id_label, niveau_classe.Code AS niveau_classe_id_label FROM formation_niveau LEFT JOIN formation ON formation_niveau.formation_id = formation.Id LEFT JOIN niveau_classe ON formation_niveau.niveau_classe_id = niveau_classe.Id ORDER BY formation_niveau.Id"
SELECT_BY_ID = "SELECT formation_niveau.*, formation.Code AS formation_id_label, niveau_classe.Code AS niveau_classe_id_label FROM formation_niveau LEFT JOIN formation ON formation_niveau.formation_id = formation.Id LEFT JOIN niveau_classe ON formation_niveau.niveau_classe_id = niveau_classe.Id WHERE formation_niveau.Id = ?"
INSERT       = "INSERT INTO formation_niveau (Code, Libelle, OrdreIndicatif, formation_id, niveau_classe_id, CreatedAt, UpdatedAt) VALUES (?, ?, ?, ?, ?, ?, ?)"
UPDATE       = "UPDATE formation_niveau SET Code = ?, Libelle = ?, OrdreIndicatif = ?, formation_id = ?, niveau_classe_id = ?, UpdatedAt = ? WHERE Id = ?"
DELETE       = "DELETE FROM formation_niveau WHERE Id = ?"


def get_formation_niveaus():
    return fetch_all(SELECT_ALL)


def get_formation_niveau_by_id(id):
    return fetch_one(SELECT_BY_ID, (id,))


def add_formation_niveau(data):
    return insert(INSERT, (data["code"], data["libelle"], data["ordre_indicatif"], data["formation_id"], data["niveau_classe_id"], datetime.now(timezone.utc), datetime.now(timezone.utc),))


def update_formation_niveau(id, data):
    execute(UPDATE, (data["code"], data["libelle"], data["ordre_indicatif"], data["formation_id"], data["niveau_classe_id"], datetime.now(timezone.utc), id))


def delete_formation_niveau(id):
    execute(DELETE, (id,))


def bulk_delete_formation_niveaus(ids):
    """Supprime plusieurs enregistrements par ID. Aucune concaténation SQL."""
    if not ids:
        return
    placeholders = ", ".join("?" for _ in ids)
    execute("DELETE FROM formation_niveau WHERE Id IN (" + placeholders + ")", list(ids))


_SEARCH_COLS  = ['formation_niveau.Code', 'formation_niveau.Libelle']
_ALLOWED_SORT = {"code": "formation_niveau.Code", "libelle": "formation_niveau.Libelle", "ordre_indicatif": "formation_niveau.OrdreIndicatif", "formation_id": "formation_niveau.formation_id", "niveau_classe_id": "formation_niveau.niveau_classe_id", "id": "formation_niveau.Id"}
_ALLOWED_FILTERS = {"formation_id": "formation_niveau.formation_id", "niveau_classe_id": "formation_niveau.niveau_classe_id"}
_DEFAULT_SORT = "formation_niveau.Id"


def count_formation_niveaus(q: str | None = None, filters: dict[str, Any] | None = None) -> int:
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
        sql = "SELECT COUNT(*) AS total FROM formation_niveau WHERE " + " AND ".join(clauses)
    else:
        sql = "SELECT COUNT(*) AS total FROM formation_niveau"
    row = fetch_one(sql, params)
    return row["total"] if row else 0


def find_formation_niveaus_paginated(q: str | None = None, sort: str | None = None, direction: str = "asc", limit: int = 10, offset: int = 0, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    sort_col = _ALLOWED_SORT.get(sort or "", _DEFAULT_SORT)
    sort_dir = "DESC" if direction == "desc" else "ASC"
    base = "SELECT formation_niveau.*, formation.Code AS formation_id_label, niveau_classe.Code AS niveau_classe_id_label FROM formation_niveau LEFT JOIN formation ON formation_niveau.formation_id = formation.Id LEFT JOIN niveau_classe ON formation_niveau.niveau_classe_id = niveau_classe.Id"
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


def find_formation_niveaus_for_export(q: str | None = None, sort: str | None = None, direction: str = "asc", filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    return find_formation_niveaus_paginated(
        q=q, sort=sort, direction=direction,
        limit=_EXPORT_LIMIT, offset=0, filters=filters,
    )



def get_formation_choices():
    rows = fetch_all("SELECT Id, Code FROM formation ORDER BY Code")
    return [(row["Id"], row["Code"]) for row in rows]


def get_niveau_classe_choices():
    rows = fetch_all("SELECT Id, Code FROM niveau_classe ORDER BY Code")
    return [(row["Id"], row["Code"]) for row in rows]