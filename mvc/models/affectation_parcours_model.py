from typing import Any

from core.database.db import fetch_one, fetch_all, execute, insert

SELECT_ALL   = "SELECT affectation_parcours.*, version_parcours.Version AS version_parcours_id_label, classe.Libelle AS classe_id_label, professeur.Nom AS professeur_id_label FROM affectation_parcours LEFT JOIN version_parcours ON affectation_parcours.version_parcours_id = version_parcours.Id LEFT JOIN classe ON affectation_parcours.classe_id = classe.Id LEFT JOIN professeur ON affectation_parcours.professeur_id = professeur.Id ORDER BY affectation_parcours.Id"
SELECT_BY_ID = "SELECT affectation_parcours.*, version_parcours.Version AS version_parcours_id_label, classe.Libelle AS classe_id_label, professeur.Nom AS professeur_id_label FROM affectation_parcours LEFT JOIN version_parcours ON affectation_parcours.version_parcours_id = version_parcours.Id LEFT JOIN classe ON affectation_parcours.classe_id = classe.Id LEFT JOIN professeur ON affectation_parcours.professeur_id = professeur.Id WHERE affectation_parcours.Id = ?"
INSERT       = "INSERT INTO affectation_parcours (DateAffectation, Statut, version_parcours_id, classe_id, professeur_id, CreatedAt, UpdatedAt) VALUES (?, ?, ?, ?, ?, ?, ?)"
UPDATE       = "UPDATE affectation_parcours SET DateAffectation = ?, Statut = ?, version_parcours_id = ?, classe_id = ?, professeur_id = ?, CreatedAt = ?, UpdatedAt = ? WHERE Id = ?"
DELETE       = "DELETE FROM affectation_parcours WHERE Id = ?"


def get_affectation_parcourss():
    return fetch_all(SELECT_ALL)


def get_affectation_parcours_by_id(id):
    return fetch_one(SELECT_BY_ID, (id,))


def add_affectation_parcours(data):
    return insert(INSERT, (data["date_affectation"], data["statut"], data["version_parcours_id"], data["classe_id"], data["professeur_id"], data["created_at"], data["updated_at"],))


def update_affectation_parcours(id, data):
    execute(UPDATE, (data["date_affectation"], data["statut"], data["version_parcours_id"], data["classe_id"], data["professeur_id"], data["created_at"], data["updated_at"], id))


def delete_affectation_parcours(id):
    execute(DELETE, (id,))


def bulk_delete_affectation_parcourss(ids):
    """Supprime plusieurs enregistrements par ID. Aucune concaténation SQL."""
    if not ids:
        return
    placeholders = ", ".join("?" for _ in ids)
    execute("DELETE FROM affectation_parcours WHERE Id IN (" + placeholders + ")", list(ids))


_SEARCH_COLS  = ['affectation_parcours.Statut']
_ALLOWED_SORT = {"date_affectation": "affectation_parcours.DateAffectation", "statut": "affectation_parcours.Statut", "version_parcours_id": "affectation_parcours.version_parcours_id", "classe_id": "affectation_parcours.classe_id", "professeur_id": "affectation_parcours.professeur_id", "created_at": "affectation_parcours.CreatedAt", "updated_at": "affectation_parcours.UpdatedAt", "id": "affectation_parcours.Id"}
_ALLOWED_FILTERS = {"version_parcours_id": "affectation_parcours.version_parcours_id", "classe_id": "affectation_parcours.classe_id", "professeur_id": "affectation_parcours.professeur_id"}
_DEFAULT_SORT = "affectation_parcours.Id"


def count_affectation_parcourss(q: str | None = None, filters: dict[str, Any] | None = None) -> int:
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
        sql = "SELECT COUNT(*) AS total FROM affectation_parcours WHERE " + " AND ".join(clauses)
    else:
        sql = "SELECT COUNT(*) AS total FROM affectation_parcours"
    row = fetch_one(sql, params)
    return row["total"] if row else 0


def find_affectation_parcourss_paginated(q: str | None = None, sort: str | None = None, direction: str = "asc", limit: int = 10, offset: int = 0, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    sort_col = _ALLOWED_SORT.get(sort or "", _DEFAULT_SORT)
    sort_dir = "DESC" if direction == "desc" else "ASC"
    base = "SELECT affectation_parcours.*, version_parcours.Version AS version_parcours_id_label, classe.Libelle AS classe_id_label, professeur.Nom AS professeur_id_label FROM affectation_parcours LEFT JOIN version_parcours ON affectation_parcours.version_parcours_id = version_parcours.Id LEFT JOIN classe ON affectation_parcours.classe_id = classe.Id LEFT JOIN professeur ON affectation_parcours.professeur_id = professeur.Id"
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


def find_affectation_parcourss_for_export(q: str | None = None, sort: str | None = None, direction: str = "asc", filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    return find_affectation_parcourss_paginated(
        q=q, sort=sort, direction=direction,
        limit=_EXPORT_LIMIT, offset=0, filters=filters,
    )



def get_version_parcours_choices():
    rows = fetch_all("SELECT Id, Version FROM version_parcours ORDER BY Version")
    return [(row["Id"], row["Version"]) for row in rows]


def get_classe_choices():
    rows = fetch_all("SELECT Id, Libelle FROM classe ORDER BY Libelle")
    return [(row["Id"], row["Libelle"]) for row in rows]


def get_professeur_choices():
    rows = fetch_all("SELECT Id, Nom FROM professeur ORDER BY Nom")
    return [(row["Id"], row["Nom"]) for row in rows]


def get_eleve_choices():
    rows = fetch_all("SELECT Id, Nom FROM eleve ORDER BY Nom")
    return [(row["Id"], row["Nom"]) for row in rows]


def get_affectation_parcours_eleve_ids(id):
    rows = fetch_all("SELECT eleve_id FROM affectation_parcours_eleve WHERE affectation_parcours_id = ?", (id,))
    return [row["eleve_id"] for row in rows]


def get_affectation_parcours_eleve_labels_by_affectation_parcours_id(ids):
    if not ids:
        return {}
    placeholders = ", ".join("?" for _ in ids)
    rows = fetch_all(
        "SELECT pivot.affectation_parcours_id AS source_id, eleve.Id AS target_id, eleve.Nom AS target_label "
        "FROM affectation_parcours_eleve pivot "
        "JOIN eleve ON eleve.Id = pivot.eleve_id "
        "WHERE pivot.affectation_parcours_id IN (" + placeholders + ") "
        "ORDER BY eleve.Nom",
        tuple(ids),
    )
    grouped = {}
    for row in rows:
        grouped.setdefault(row["source_id"], []).append(row["target_label"])
    return grouped


def get_affectation_parcours_eleve_labels(id):
    rows = fetch_all(
        "SELECT eleve.Id AS target_id, eleve.Nom AS target_label "
        "FROM affectation_parcours_eleve pivot "
        "JOIN eleve ON eleve.Id = pivot.eleve_id "
        "WHERE pivot.affectation_parcours_id = ? "
        "ORDER BY eleve.Nom",
        (id,),
    )
    return [row["target_label"] for row in rows]


def add_affectation_parcours_eleve_ids(id, selected_ids):
    from core.database.transaction import transaction
    with transaction() as tx:
        for target_id in selected_ids:
            execute("INSERT INTO affectation_parcours_eleve (affectation_parcours_id, eleve_id) VALUES (?, ?)", (id, target_id), tx=tx)


def sync_affectation_parcours_eleve_ids(id, selected_ids):
    from core.database.transaction import transaction
    with transaction() as tx:
        execute("DELETE FROM affectation_parcours_eleve WHERE affectation_parcours_id = ?", (id,), tx=tx)
        for target_id in selected_ids:
            execute("INSERT INTO affectation_parcours_eleve (affectation_parcours_id, eleve_id) VALUES (?, ?)", (id, target_id), tx=tx)