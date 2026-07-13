from datetime import datetime, timezone

from typing import Any

from core.database.db import fetch_one, fetch_all, execute, insert

SELECT_ALL   = "SELECT activite_professionnelle.*, referentiel_niveau_classe.Identifiant AS referentiel_id_label, pole_activite.Intitule AS pole_id_label FROM activite_professionnelle LEFT JOIN referentiel_niveau_classe ON activite_professionnelle.referentiel_id = referentiel_niveau_classe.Id LEFT JOIN pole_activite ON activite_professionnelle.pole_id = pole_activite.Id ORDER BY activite_professionnelle.Id"
SELECT_BY_ID = "SELECT activite_professionnelle.*, referentiel_niveau_classe.Identifiant AS referentiel_id_label, pole_activite.Intitule AS pole_id_label FROM activite_professionnelle LEFT JOIN referentiel_niveau_classe ON activite_professionnelle.referentiel_id = referentiel_niveau_classe.Id LEFT JOIN pole_activite ON activite_professionnelle.pole_id = pole_activite.Id WHERE activite_professionnelle.Id = ?"
INSERT       = "INSERT INTO activite_professionnelle (Code, Intitule, ConditionsExercice, referentiel_id, pole_id, CreatedAt, UpdatedAt) VALUES (?, ?, ?, ?, ?, ?, ?)"
UPDATE       = "UPDATE activite_professionnelle SET Code = ?, Intitule = ?, ConditionsExercice = ?, referentiel_id = ?, pole_id = ?, UpdatedAt = ? WHERE Id = ?"
DELETE       = "DELETE FROM activite_professionnelle WHERE Id = ?"


def get_activite_professionnelles():
    return fetch_all(SELECT_ALL)


def get_activite_professionnelle_by_id(id):
    return fetch_one(SELECT_BY_ID, (id,))


def add_activite_professionnelle(data):
    return insert(INSERT, (data["code"], data["intitule"], data["conditions_exercice"], data["referentiel_id"], data["pole_id"], datetime.now(timezone.utc), datetime.now(timezone.utc),))


def update_activite_professionnelle(id, data):
    execute(UPDATE, (data["code"], data["intitule"], data["conditions_exercice"], data["referentiel_id"], data["pole_id"], datetime.now(timezone.utc), id))


def delete_activite_professionnelle(id):
    execute(DELETE, (id,))


def bulk_delete_activite_professionnelles(ids):
    """Supprime plusieurs enregistrements par ID. Aucune concaténation SQL."""
    if not ids:
        return
    placeholders = ", ".join("?" for _ in ids)
    execute("DELETE FROM activite_professionnelle WHERE Id IN (" + placeholders + ")", list(ids))


_SEARCH_COLS  = ['activite_professionnelle.Code', 'activite_professionnelle.Intitule', 'activite_professionnelle.ConditionsExercice']
_ALLOWED_SORT = {"code": "activite_professionnelle.Code", "intitule": "activite_professionnelle.Intitule", "conditions_exercice": "activite_professionnelle.ConditionsExercice", "referentiel_id": "activite_professionnelle.referentiel_id", "pole_id": "activite_professionnelle.pole_id", "created_at": "activite_professionnelle.CreatedAt", "updated_at": "activite_professionnelle.UpdatedAt", "id": "activite_professionnelle.Id"}
_ALLOWED_FILTERS = {"referentiel_id": "activite_professionnelle.referentiel_id", "pole_id": "activite_professionnelle.pole_id"}
_DEFAULT_SORT = "activite_professionnelle.Id"


def count_activite_professionnelles(q: str | None = None, filters: dict[str, Any] | None = None) -> int:
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
        sql = "SELECT COUNT(*) AS total FROM activite_professionnelle WHERE " + " AND ".join(clauses)
    else:
        sql = "SELECT COUNT(*) AS total FROM activite_professionnelle"
    row = fetch_one(sql, params)
    return row["total"] if row else 0


def find_activite_professionnelles_paginated(q: str | None = None, sort: str | None = None, direction: str = "asc", limit: int = 10, offset: int = 0, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    sort_col = _ALLOWED_SORT.get(sort or "", _DEFAULT_SORT)
    sort_dir = "DESC" if direction == "desc" else "ASC"
    base = "SELECT activite_professionnelle.*, referentiel_niveau_classe.Identifiant AS referentiel_id_label, pole_activite.Intitule AS pole_id_label FROM activite_professionnelle LEFT JOIN referentiel_niveau_classe ON activite_professionnelle.referentiel_id = referentiel_niveau_classe.Id LEFT JOIN pole_activite ON activite_professionnelle.pole_id = pole_activite.Id"
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


def find_activite_professionnelles_for_export(q: str | None = None, sort: str | None = None, direction: str = "asc", filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    return find_activite_professionnelles_paginated(
        q=q, sort=sort, direction=direction,
        limit=_EXPORT_LIMIT, offset=0, filters=filters,
    )



def get_referentiel_niveau_classe_choices():
    rows = fetch_all("SELECT Id, Identifiant FROM referentiel_niveau_classe ORDER BY Identifiant")
    return [(row["Id"], row["Identifiant"]) for row in rows]


def get_pole_activite_choices():
    rows = fetch_all("SELECT Id, Intitule FROM pole_activite ORDER BY Intitule")
    return [(row["Id"], row["Intitule"]) for row in rows]


def get_competence_choices():
    rows = fetch_all("SELECT Id, Code FROM competence ORDER BY Code")
    return [(row["Id"], row["Code"]) for row in rows]


def get_activite_professionnelle_competence_ids(id):
    rows = fetch_all("SELECT competence_id FROM activite_competence WHERE activite_professionnelle_id = ?", (id,))
    return [row["competence_id"] for row in rows]


def get_activite_professionnelle_competence_labels_by_activite_professionnelle_id(ids):
    if not ids:
        return {}
    placeholders = ", ".join("?" for _ in ids)
    rows = fetch_all(
        "SELECT pivot.activite_professionnelle_id AS source_id, competence.Id AS target_id, competence.Code AS target_label "
        "FROM activite_competence pivot "
        "JOIN competence ON competence.Id = pivot.competence_id "
        "WHERE pivot.activite_professionnelle_id IN (" + placeholders + ") "
        "ORDER BY competence.Code",
        tuple(ids),
    )
    grouped = {}
    for row in rows:
        grouped.setdefault(row["source_id"], []).append(row["target_label"])
    return grouped


def get_activite_professionnelle_competence_labels(id):
    rows = fetch_all(
        "SELECT competence.Id AS target_id, competence.Code AS target_label "
        "FROM activite_competence pivot "
        "JOIN competence ON competence.Id = pivot.competence_id "
        "WHERE pivot.activite_professionnelle_id = ? "
        "ORDER BY competence.Code",
        (id,),
    )
    return [row["target_label"] for row in rows]


def add_activite_professionnelle_competence_ids(id, selected_ids):
    from core.database.transaction import transaction
    with transaction() as tx:
        for target_id in selected_ids:
            execute("INSERT INTO activite_competence (activite_professionnelle_id, competence_id) VALUES (?, ?)", (id, target_id), tx=tx)


def sync_activite_professionnelle_competence_ids(id, selected_ids):
    from core.database.transaction import transaction
    with transaction() as tx:
        execute("DELETE FROM activite_competence WHERE activite_professionnelle_id = ?", (id,), tx=tx)
        for target_id in selected_ids:
            execute("INSERT INTO activite_competence (activite_professionnelle_id, competence_id) VALUES (?, ?)", (id, target_id), tx=tx)