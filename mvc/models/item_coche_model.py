from typing import Any

from core.database.db import fetch_one, fetch_all, execute, insert

SELECT_ALL   = "SELECT item_coche.*, item_checklist.Libelle AS item_id_label, progression_palier.Statut AS progression_palier_id_label FROM item_coche LEFT JOIN item_checklist ON item_coche.item_id = item_checklist.Id LEFT JOIN progression_palier ON item_coche.progression_palier_id = progression_palier.Id ORDER BY item_coche.Id"
SELECT_BY_ID = "SELECT item_coche.*, item_checklist.Libelle AS item_id_label, progression_palier.Statut AS progression_palier_id_label FROM item_coche LEFT JOIN item_checklist ON item_coche.item_id = item_checklist.Id LEFT JOIN progression_palier ON item_coche.progression_palier_id = progression_palier.Id WHERE item_coche.Id = ?"
INSERT       = "INSERT INTO item_coche (CocheEleve, CocheProfesseur, item_id, progression_palier_id) VALUES (?, ?, ?, ?)"
UPDATE       = "UPDATE item_coche SET CocheEleve = ?, CocheProfesseur = ?, item_id = ?, progression_palier_id = ? WHERE Id = ?"
DELETE       = "DELETE FROM item_coche WHERE Id = ?"


def get_item_coches():
    return fetch_all(SELECT_ALL)


def get_item_coche_by_id(id):
    return fetch_one(SELECT_BY_ID, (id,))


def add_item_coche(data):
    return insert(INSERT, (data["coche_eleve"], data["coche_professeur"], data["item_id"], data["progression_palier_id"], ))


def update_item_coche(id, data):
    execute(UPDATE, (data["coche_eleve"], data["coche_professeur"], data["item_id"], data["progression_palier_id"], id))


def delete_item_coche(id):
    execute(DELETE, (id,))


def bulk_delete_item_coches(ids):
    """Supprime plusieurs enregistrements par ID. Aucune concaténation SQL."""
    if not ids:
        return
    placeholders = ", ".join("?" for _ in ids)
    execute("DELETE FROM item_coche WHERE Id IN (" + placeholders + ")", list(ids))


_SEARCH_COLS  = []
_ALLOWED_SORT = {"coche_eleve": "item_coche.CocheEleve", "coche_professeur": "item_coche.CocheProfesseur", "item_id": "item_coche.item_id", "progression_palier_id": "item_coche.progression_palier_id", "created_at": "item_coche.CreatedAt", "updated_at": "item_coche.UpdatedAt", "id": "item_coche.Id"}
_ALLOWED_FILTERS = {"item_id": "item_coche.item_id", "progression_palier_id": "item_coche.progression_palier_id"}
_DEFAULT_SORT = "item_coche.Id"


def count_item_coches(q: str | None = None, filters: dict[str, Any] | None = None) -> int:
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
        sql = "SELECT COUNT(*) AS total FROM item_coche WHERE " + " AND ".join(clauses)
    else:
        sql = "SELECT COUNT(*) AS total FROM item_coche"
    row = fetch_one(sql, params)
    return row["total"] if row else 0


def find_item_coches_paginated(q: str | None = None, sort: str | None = None, direction: str = "asc", limit: int = 10, offset: int = 0, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    sort_col = _ALLOWED_SORT.get(sort or "", _DEFAULT_SORT)
    sort_dir = "DESC" if direction == "desc" else "ASC"
    base = "SELECT item_coche.*, item_checklist.Libelle AS item_id_label, progression_palier.Statut AS progression_palier_id_label FROM item_coche LEFT JOIN item_checklist ON item_coche.item_id = item_checklist.Id LEFT JOIN progression_palier ON item_coche.progression_palier_id = progression_palier.Id"
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


def find_item_coches_for_export(q: str | None = None, sort: str | None = None, direction: str = "asc", filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    return find_item_coches_paginated(
        q=q, sort=sort, direction=direction,
        limit=_EXPORT_LIMIT, offset=0, filters=filters,
    )



def get_item_checklist_choices():
    rows = fetch_all("SELECT Id, Libelle FROM item_checklist ORDER BY Libelle")
    return [(row["Id"], row["Libelle"]) for row in rows]


def get_progression_palier_choices():
    rows = fetch_all("SELECT Id, Statut FROM progression_palier ORDER BY Statut")
    return [(row["Id"], row["Statut"]) for row in rows]