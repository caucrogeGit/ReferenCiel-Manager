from typing import Any

from core.database.db import fetch_one, fetch_all, execute, insert

SELECT_ALL   = "SELECT palier.*, version_parcours.Version AS version_parcours_id_label FROM palier LEFT JOIN version_parcours ON palier.version_parcours_id = version_parcours.Id ORDER BY palier.Id"
SELECT_BY_ID = "SELECT palier.*, version_parcours.Version AS version_parcours_id_label FROM palier LEFT JOIN version_parcours ON palier.version_parcours_id = version_parcours.Id WHERE palier.Id = ?"
INSERT       = "INSERT INTO palier (Ordre, Titre, Theme, ProductionAttendue, DossierTechniqueFichier, version_parcours_id) VALUES (?, ?, ?, ?, ?, ?)"
UPDATE       = "UPDATE palier SET Ordre = ?, Titre = ?, Theme = ?, ProductionAttendue = ?, DossierTechniqueFichier = ?, version_parcours_id = ? WHERE Id = ?"
DELETE       = "DELETE FROM palier WHERE Id = ?"


def get_paliers():
    return fetch_all(SELECT_ALL)


def get_palier_by_id(id):
    return fetch_one(SELECT_BY_ID, (id,))


def add_palier(data):
    return insert(INSERT, (data["ordre"], data["titre"], data["theme"], data["production_attendue"], data["dossier_technique_fichier"], data["version_parcours_id"], ))


def update_palier(id, data):
    execute(UPDATE, (data["ordre"], data["titre"], data["theme"], data["production_attendue"], data["dossier_technique_fichier"], data["version_parcours_id"], id))


def delete_palier(id):
    execute(DELETE, (id,))


def bulk_delete_paliers(ids):
    """Supprime plusieurs enregistrements par ID. Aucune concaténation SQL."""
    if not ids:
        return
    placeholders = ", ".join("?" for _ in ids)
    execute("DELETE FROM palier WHERE Id IN (" + placeholders + ")", list(ids))


_SEARCH_COLS  = ['palier.Titre', 'palier.Theme', 'palier.ProductionAttendue', 'palier.DossierTechniqueFichier']
_ALLOWED_SORT = {"ordre": "palier.Ordre", "titre": "palier.Titre", "theme": "palier.Theme", "production_attendue": "palier.ProductionAttendue", "dossier_technique_fichier": "palier.DossierTechniqueFichier", "version_parcours_id": "palier.version_parcours_id", "created_at": "palier.CreatedAt", "updated_at": "palier.UpdatedAt", "id": "palier.Id"}
_ALLOWED_FILTERS = {"version_parcours_id": "palier.version_parcours_id"}
_DEFAULT_SORT = "palier.Id"


def count_paliers(q: str | None = None, filters: dict[str, Any] | None = None) -> int:
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
        sql = "SELECT COUNT(*) AS total FROM palier WHERE " + " AND ".join(clauses)
    else:
        sql = "SELECT COUNT(*) AS total FROM palier"
    row = fetch_one(sql, params)
    return row["total"] if row else 0


def find_paliers_paginated(q: str | None = None, sort: str | None = None, direction: str = "asc", limit: int = 10, offset: int = 0, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    sort_col = _ALLOWED_SORT.get(sort or "", _DEFAULT_SORT)
    sort_dir = "DESC" if direction == "desc" else "ASC"
    base = "SELECT palier.*, version_parcours.Version AS version_parcours_id_label FROM palier LEFT JOIN version_parcours ON palier.version_parcours_id = version_parcours.Id"
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


def find_paliers_for_export(q: str | None = None, sort: str | None = None, direction: str = "asc", filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    return find_paliers_paginated(
        q=q, sort=sort, direction=direction,
        limit=_EXPORT_LIMIT, offset=0, filters=filters,
    )



def get_version_parcours_choices():
    rows = fetch_all("SELECT Id, Version FROM version_parcours ORDER BY Version")
    return [(row["Id"], row["Version"]) for row in rows]