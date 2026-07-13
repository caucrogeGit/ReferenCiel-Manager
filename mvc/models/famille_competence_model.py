from datetime import datetime, timezone

from typing import Any

from core.database.db import fetch_one, fetch_all, execute, insert

SELECT_ALL   = "SELECT famille_competence.*, referentiel_niveau_classe.Identifiant AS referentiel_id_label FROM famille_competence LEFT JOIN referentiel_niveau_classe ON famille_competence.referentiel_id = referentiel_niveau_classe.Id ORDER BY famille_competence.Id"
SELECT_BY_ID = "SELECT famille_competence.*, referentiel_niveau_classe.Identifiant AS referentiel_id_label FROM famille_competence LEFT JOIN referentiel_niveau_classe ON famille_competence.referentiel_id = referentiel_niveau_classe.Id WHERE famille_competence.Id = ?"
INSERT       = "INSERT INTO famille_competence (Code, Intitule, referentiel_id, CreatedAt, UpdatedAt) VALUES (?, ?, ?, ?, ?)"
UPDATE       = "UPDATE famille_competence SET Code = ?, Intitule = ?, referentiel_id = ?, UpdatedAt = ? WHERE Id = ?"
DELETE       = "DELETE FROM famille_competence WHERE Id = ?"


def get_famille_competences():
    return fetch_all(SELECT_ALL)


def get_famille_competence_by_id(id):
    return fetch_one(SELECT_BY_ID, (id,))


def add_famille_competence(data):
    return insert(INSERT, (data["code"], data["intitule"], data["referentiel_id"], datetime.now(timezone.utc), datetime.now(timezone.utc),))


def update_famille_competence(id, data):
    execute(UPDATE, (data["code"], data["intitule"], data["referentiel_id"], datetime.now(timezone.utc), id))


def delete_famille_competence(id):
    execute(DELETE, (id,))


def bulk_delete_famille_competences(ids):
    """Supprime plusieurs enregistrements par ID. Aucune concaténation SQL."""
    if not ids:
        return
    placeholders = ", ".join("?" for _ in ids)
    execute("DELETE FROM famille_competence WHERE Id IN (" + placeholders + ")", list(ids))


_SEARCH_COLS  = ['famille_competence.Code', 'famille_competence.Intitule']
_ALLOWED_SORT = {"code": "famille_competence.Code", "intitule": "famille_competence.Intitule", "referentiel_id": "famille_competence.referentiel_id", "created_at": "famille_competence.CreatedAt", "updated_at": "famille_competence.UpdatedAt", "id": "famille_competence.Id"}
_ALLOWED_FILTERS = {"referentiel_id": "famille_competence.referentiel_id"}
_DEFAULT_SORT = "famille_competence.Id"


def count_famille_competences(q: str | None = None, filters: dict[str, Any] | None = None) -> int:
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
        sql = "SELECT COUNT(*) AS total FROM famille_competence WHERE " + " AND ".join(clauses)
    else:
        sql = "SELECT COUNT(*) AS total FROM famille_competence"
    row = fetch_one(sql, params)
    return row["total"] if row else 0


def find_famille_competences_paginated(q: str | None = None, sort: str | None = None, direction: str = "asc", limit: int = 10, offset: int = 0, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    sort_col = _ALLOWED_SORT.get(sort or "", _DEFAULT_SORT)
    sort_dir = "DESC" if direction == "desc" else "ASC"
    base = "SELECT famille_competence.*, referentiel_niveau_classe.Identifiant AS referentiel_id_label FROM famille_competence LEFT JOIN referentiel_niveau_classe ON famille_competence.referentiel_id = referentiel_niveau_classe.Id"
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


def find_famille_competences_for_export(q: str | None = None, sort: str | None = None, direction: str = "asc", filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    return find_famille_competences_paginated(
        q=q, sort=sort, direction=direction,
        limit=_EXPORT_LIMIT, offset=0, filters=filters,
    )



def get_referentiel_niveau_classe_choices():
    rows = fetch_all("SELECT Id, Identifiant FROM referentiel_niveau_classe ORDER BY Identifiant")
    return [(row["Id"], row["Identifiant"]) for row in rows]


def get_competence_choices():
    rows = fetch_all("SELECT Id, Code FROM competence ORDER BY Code")
    return [(row["Id"], row["Code"]) for row in rows]


def get_famille_competence_competence_ids(id):
    rows = fetch_all("SELECT competence_id FROM cc_competence WHERE famille_competence_id = ?", (id,))
    return [row["competence_id"] for row in rows]


def get_famille_competence_competence_labels_by_famille_competence_id(ids):
    if not ids:
        return {}
    placeholders = ", ".join("?" for _ in ids)
    rows = fetch_all(
        "SELECT pivot.famille_competence_id AS source_id, competence.Id AS target_id, competence.Code AS target_label "
        "FROM cc_competence pivot "
        "JOIN competence ON competence.Id = pivot.competence_id "
        "WHERE pivot.famille_competence_id IN (" + placeholders + ") "
        "ORDER BY competence.Code",
        tuple(ids),
    )
    grouped = {}
    for row in rows:
        grouped.setdefault(row["source_id"], []).append(row["target_label"])
    return grouped


def get_famille_competence_competence_labels(id):
    rows = fetch_all(
        "SELECT competence.Id AS target_id, competence.Code AS target_label "
        "FROM cc_competence pivot "
        "JOIN competence ON competence.Id = pivot.competence_id "
        "WHERE pivot.famille_competence_id = ? "
        "ORDER BY competence.Code",
        (id,),
    )
    return [row["target_label"] for row in rows]


def add_famille_competence_competence_ids(id, selected_ids):
    from core.database.transaction import transaction
    with transaction() as tx:
        for target_id in selected_ids:
            execute("INSERT INTO cc_competence (famille_competence_id, competence_id) VALUES (?, ?)", (id, target_id), tx=tx)


def sync_famille_competence_competence_ids(id, selected_ids):
    from core.database.transaction import transaction
    with transaction() as tx:
        execute("DELETE FROM cc_competence WHERE famille_competence_id = ?", (id,), tx=tx)
        for target_id in selected_ids:
            execute("INSERT INTO cc_competence (famille_competence_id, competence_id) VALUES (?, ?)", (id, target_id), tx=tx)