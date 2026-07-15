from datetime import datetime, timezone

from typing import Any

from core.database.db import fetch_one, fetch_all, execute, insert

SELECT_ALL   = "SELECT classe.*, annee_scolaire.Libelle AS annee_scolaire_id_label, formation_niveau.Libelle AS formation_niveau_id_label FROM classe LEFT JOIN annee_scolaire ON classe.annee_scolaire_id = annee_scolaire.Id LEFT JOIN formation_niveau ON classe.formation_niveau_id = formation_niveau.Id ORDER BY classe.Id"
SELECT_BY_ID = "SELECT * FROM classe WHERE Id = ?"
INSERT       = "INSERT INTO classe (Code, Libelle, CreatedAt, UpdatedAt, annee_scolaire_id, formation_niveau_id) VALUES (?, ?, ?, ?, ?, ?)"
UPDATE       = "UPDATE classe SET Code = ?, Libelle = ?, UpdatedAt = ?, annee_scolaire_id = ?, formation_niveau_id = ? WHERE Id = ?"
DELETE       = "DELETE FROM classe WHERE Id = ?"


def get_classes():
    return fetch_all(SELECT_ALL)


def get_classe_by_id(id):
    return fetch_one(SELECT_BY_ID, (id,))


def add_classe(data):
    return insert(INSERT, (data["code"], data["libelle"], datetime.now(timezone.utc), datetime.now(timezone.utc), data["annee_scolaire_id"], data["formation_niveau_id"],))


def update_classe(id, data):
    execute(UPDATE, (data["code"], data["libelle"], datetime.now(timezone.utc), data["annee_scolaire_id"], data["formation_niveau_id"], id))


def delete_classe(id):
    execute(DELETE, (id,))


def bulk_delete_classes(ids):
    """Supprime plusieurs enregistrements par ID. Aucune concaténation SQL."""
    if not ids:
        return
    placeholders = ", ".join("?" for _ in ids)
    execute("DELETE FROM classe WHERE Id IN (" + placeholders + ")", list(ids))


_SEARCH_COLS  = ['classe.Code', 'classe.Libelle']
_ALLOWED_SORT = {"code": "classe.Code", "libelle": "classe.Libelle", "created_at": "classe.CreatedAt", "updated_at": "classe.UpdatedAt", "annee_scolaire_id": "classe.annee_scolaire_id", "formation_niveau_id": "classe.formation_niveau_id", "id": "classe.Id"}
_ALLOWED_FILTERS = {"annee_scolaire_id": "classe.annee_scolaire_id", "formation_niveau_id": "classe.formation_niveau_id"}
_DEFAULT_SORT = "classe.Id"


def count_classes(q: str | None = None, filters: dict[str, Any] | None = None) -> int:
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
        sql = "SELECT COUNT(*) AS total FROM classe WHERE " + " AND ".join(clauses)
    else:
        sql = "SELECT COUNT(*) AS total FROM classe"
    row = fetch_one(sql, params)
    return row["total"] if row else 0


def find_classes_paginated(q: str | None = None, sort: str | None = None, direction: str = "asc", limit: int = 10, offset: int = 0, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    sort_col = _ALLOWED_SORT.get(sort or "", _DEFAULT_SORT)
    sort_dir = "DESC" if direction == "desc" else "ASC"
    base = "SELECT classe.*, annee_scolaire.Libelle AS annee_scolaire_id_label, formation_niveau.Libelle AS formation_niveau_id_label FROM classe LEFT JOIN annee_scolaire ON classe.annee_scolaire_id = annee_scolaire.Id LEFT JOIN formation_niveau ON classe.formation_niveau_id = formation_niveau.Id"
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


def find_classes_for_export(q: str | None = None, sort: str | None = None, direction: str = "asc", filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    return find_classes_paginated(
        q=q, sort=sort, direction=direction,
        limit=_EXPORT_LIMIT, offset=0, filters=filters,
    )



def get_annee_scolaire_choices():
    rows = fetch_all("SELECT Id, Libelle FROM annee_scolaire ORDER BY Libelle")
    return [(row["Id"], row["Libelle"]) for row in rows]


def get_formation_niveau_choices():
    rows = fetch_all("SELECT Id, Libelle FROM formation_niveau ORDER BY OrdreIndicatif, Libelle")
    return [(row["Id"], row["Libelle"]) for row in rows]