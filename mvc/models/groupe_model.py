from typing import Any

from core.database.db import fetch_one, fetch_all, execute, insert

SELECT_ALL   = "SELECT groupe.*, classe.Libelle AS classe_id_label FROM groupe LEFT JOIN classe ON groupe.classe_id = classe.Id ORDER BY groupe.Id"
SELECT_BY_ID = "SELECT groupe.*, classe.Libelle AS classe_id_label FROM groupe LEFT JOIN classe ON groupe.classe_id = classe.Id WHERE groupe.Id = ?"
INSERT       = "INSERT INTO groupe (Nom, classe_id, CreatedAt, UpdatedAt) VALUES (?, ?, ?, ?)"
UPDATE       = "UPDATE groupe SET Nom = ?, classe_id = ?, CreatedAt = ?, UpdatedAt = ? WHERE Id = ?"
DELETE       = "DELETE FROM groupe WHERE Id = ?"


def get_groupes():
    return fetch_all(SELECT_ALL)


def get_groupe_by_id(id):
    return fetch_one(SELECT_BY_ID, (id,))


def add_groupe(data):
    return insert(INSERT, (data["nom"], data["classe_id"], data["created_at"], data["updated_at"],))


def update_groupe(id, data):
    execute(UPDATE, (data["nom"], data["classe_id"], data["created_at"], data["updated_at"], id))


def delete_groupe(id):
    execute(DELETE, (id,))


def bulk_delete_groupes(ids):
    """Supprime plusieurs enregistrements par ID. Aucune concaténation SQL."""
    if not ids:
        return
    placeholders = ", ".join("?" for _ in ids)
    execute("DELETE FROM groupe WHERE Id IN (" + placeholders + ")", list(ids))


_SEARCH_COLS  = ['groupe.Nom']
_ALLOWED_SORT = {"nom": "groupe.Nom", "classe_id": "groupe.classe_id", "created_at": "groupe.CreatedAt", "updated_at": "groupe.UpdatedAt", "id": "groupe.Id"}
_ALLOWED_FILTERS = {"classe_id": "groupe.classe_id"}
_DEFAULT_SORT = "groupe.Id"


def count_groupes(q: str | None = None, filters: dict[str, Any] | None = None) -> int:
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
        sql = "SELECT COUNT(*) AS total FROM groupe WHERE " + " AND ".join(clauses)
    else:
        sql = "SELECT COUNT(*) AS total FROM groupe"
    row = fetch_one(sql, params)
    return row["total"] if row else 0


def find_groupes_paginated(q: str | None = None, sort: str | None = None, direction: str = "asc", limit: int = 10, offset: int = 0, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    sort_col = _ALLOWED_SORT.get(sort or "", _DEFAULT_SORT)
    sort_dir = "DESC" if direction == "desc" else "ASC"
    base = "SELECT groupe.*, classe.Libelle AS classe_id_label FROM groupe LEFT JOIN classe ON groupe.classe_id = classe.Id"
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


def find_groupes_for_export(q: str | None = None, sort: str | None = None, direction: str = "asc", filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    return find_groupes_paginated(
        q=q, sort=sort, direction=direction,
        limit=_EXPORT_LIMIT, offset=0, filters=filters,
    )



def get_classe_choices():
    rows = fetch_all("SELECT Id, Libelle FROM classe ORDER BY Libelle")
    return [(row["Id"], row["Libelle"]) for row in rows]


def get_eleve_choices():
    rows = fetch_all("SELECT Id, Nom FROM eleve ORDER BY Nom")
    return [(row["Id"], row["Nom"]) for row in rows]


def get_groupe_eleve_ids(id):
    rows = fetch_all("SELECT eleve_id FROM groupe_eleve WHERE groupe_id = ?", (id,))
    return [row["eleve_id"] for row in rows]


def get_groupe_eleve_labels_by_groupe_id(ids):
    if not ids:
        return {}
    placeholders = ", ".join("?" for _ in ids)
    rows = fetch_all(
        "SELECT pivot.groupe_id AS source_id, eleve.Id AS target_id, eleve.Nom AS target_label "
        "FROM groupe_eleve pivot "
        "JOIN eleve ON eleve.Id = pivot.eleve_id "
        "WHERE pivot.groupe_id IN (" + placeholders + ") "
        "ORDER BY eleve.Nom",
        tuple(ids),
    )
    grouped = {}
    for row in rows:
        grouped.setdefault(row["source_id"], []).append(row["target_label"])
    return grouped


def get_groupe_eleve_labels(id):
    rows = fetch_all(
        "SELECT eleve.Id AS target_id, eleve.Nom AS target_label "
        "FROM groupe_eleve pivot "
        "JOIN eleve ON eleve.Id = pivot.eleve_id "
        "WHERE pivot.groupe_id = ? "
        "ORDER BY eleve.Nom",
        (id,),
    )
    return [row["target_label"] for row in rows]


def add_groupe_eleve_ids(id, selected_ids):
    from core.database.transaction import transaction
    with transaction() as tx:
        for target_id in selected_ids:
            execute("INSERT INTO groupe_eleve (groupe_id, eleve_id) VALUES (?, ?)", (id, target_id), tx=tx)


def sync_groupe_eleve_ids(id, selected_ids):
    from core.database.transaction import transaction
    with transaction() as tx:
        execute("DELETE FROM groupe_eleve WHERE groupe_id = ?", (id,), tx=tx)
        for target_id in selected_ids:
            execute("INSERT INTO groupe_eleve (groupe_id, eleve_id) VALUES (?, ?)", (id, target_id), tx=tx)