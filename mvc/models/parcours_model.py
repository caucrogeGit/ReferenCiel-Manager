from datetime import datetime, timezone

from typing import Any

from core.database.db import fetch_one, fetch_all, execute, insert

SELECT_ALL   = "SELECT parcours.*, niveau_classe.Code AS niveau_classe_id_label FROM parcours LEFT JOIN niveau_classe ON parcours.niveau_classe_id = niveau_classe.Id ORDER BY parcours.Id"
SELECT_BY_ID = "SELECT parcours.*, niveau_classe.Code AS niveau_classe_id_label FROM parcours LEFT JOIN niveau_classe ON parcours.niveau_classe_id = niveau_classe.Id WHERE parcours.Id = ?"
INSERT       = "INSERT INTO parcours (Identifiant, Titre, Presentation, Statut, ActiviteGlissante, OrdreImpose, niveau_classe_id, CreatedAt, UpdatedAt) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
UPDATE       = "UPDATE parcours SET Identifiant = ?, Titre = ?, Presentation = ?, Statut = ?, ActiviteGlissante = ?, OrdreImpose = ?, niveau_classe_id = ?, UpdatedAt = ? WHERE Id = ?"
DELETE       = "DELETE FROM parcours WHERE Id = ?"


def get_parcourss():
    return fetch_all(SELECT_ALL)


def get_parcours_by_id(id):
    return fetch_one(SELECT_BY_ID, (id,))


def add_parcours(data):
    return insert(INSERT, (data["identifiant"], data["titre"], data["presentation"], data["statut"], data["activite_glissante"], data["ordre_impose"], data["niveau_classe_id"], datetime.now(timezone.utc), datetime.now(timezone.utc),))


def update_parcours(id, data):
    execute(UPDATE, (data["identifiant"], data["titre"], data["presentation"], data["statut"], data["activite_glissante"], data["ordre_impose"], data["niveau_classe_id"], datetime.now(timezone.utc), id))


def delete_parcours(id):
    execute(DELETE, (id,))


def bulk_delete_parcourss(ids):
    """Supprime plusieurs enregistrements par ID. Aucune concaténation SQL."""
    if not ids:
        return
    placeholders = ", ".join("?" for _ in ids)
    execute("DELETE FROM parcours WHERE Id IN (" + placeholders + ")", list(ids))


_SEARCH_COLS  = ['parcours.Identifiant', 'parcours.Titre', 'parcours.Presentation', 'parcours.Statut']
_ALLOWED_SORT = {"identifiant": "parcours.Identifiant", "titre": "parcours.Titre", "presentation": "parcours.Presentation", "statut": "parcours.Statut", "activite_glissante": "parcours.ActiviteGlissante", "ordre_impose": "parcours.OrdreImpose", "niveau_classe_id": "parcours.niveau_classe_id", "id": "parcours.Id"}
_ALLOWED_FILTERS = {"niveau_classe_id": "parcours.niveau_classe_id"}
_DEFAULT_SORT = "parcours.Id"


def count_parcourss(q: str | None = None, filters: dict[str, Any] | None = None) -> int:
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
        sql = "SELECT COUNT(*) AS total FROM parcours WHERE " + " AND ".join(clauses)
    else:
        sql = "SELECT COUNT(*) AS total FROM parcours"
    row = fetch_one(sql, params)
    return row["total"] if row else 0


def find_parcourss_paginated(q: str | None = None, sort: str | None = None, direction: str = "asc", limit: int = 10, offset: int = 0, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    sort_col = _ALLOWED_SORT.get(sort or "", _DEFAULT_SORT)
    sort_dir = "DESC" if direction == "desc" else "ASC"
    base = "SELECT parcours.*, niveau_classe.Code AS niveau_classe_id_label FROM parcours LEFT JOIN niveau_classe ON parcours.niveau_classe_id = niveau_classe.Id"
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


def find_parcourss_for_export(q: str | None = None, sort: str | None = None, direction: str = "asc", filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    return find_parcourss_paginated(
        q=q, sort=sort, direction=direction,
        limit=_EXPORT_LIMIT, offset=0, filters=filters,
    )



def get_niveau_classe_choices():
    rows = fetch_all("SELECT Id, Code FROM niveau_classe ORDER BY Code")
    return [(row["Id"], row["Code"]) for row in rows]