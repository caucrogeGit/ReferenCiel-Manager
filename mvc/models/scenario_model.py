from datetime import datetime, timezone

from typing import Any

from core.database.db import fetch_one, fetch_all, execute, insert

SELECT_ALL   = "SELECT scenario.*, referentiel_niveau_classe.Identifiant AS referentiel_id_label, professeur.Nom AS auteur_id_label FROM scenario LEFT JOIN referentiel_niveau_classe ON scenario.referentiel_id = referentiel_niveau_classe.Id LEFT JOIN professeur ON scenario.auteur_id = professeur.Id ORDER BY scenario.Id"
SELECT_BY_ID = "SELECT scenario.*, referentiel_niveau_classe.Identifiant AS referentiel_id_label, professeur.Nom AS auteur_id_label FROM scenario LEFT JOIN referentiel_niveau_classe ON scenario.referentiel_id = referentiel_niveau_classe.Id LEFT JOIN professeur ON scenario.auteur_id = professeur.Id WHERE scenario.Id = ?"
INSERT       = "INSERT INTO scenario (Titre, Intention, Objectifs, Statut, Version, referentiel_id, auteur_id, CreatedAt, UpdatedAt) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
UPDATE       = "UPDATE scenario SET Titre = ?, Intention = ?, Objectifs = ?, Statut = ?, Version = ?, referentiel_id = ?, auteur_id = ?, UpdatedAt = ? WHERE Id = ?"
DELETE       = "DELETE FROM scenario WHERE Id = ?"


def get_scenarios():
    return fetch_all(SELECT_ALL)


def get_scenario_by_id(id):
    return fetch_one(SELECT_BY_ID, (id,))


def add_scenario(data):
    return insert(INSERT, (data["titre"], data["intention"], data["objectifs"], data["statut"], data["version"], data["referentiel_id"], data["auteur_id"], datetime.now(timezone.utc), datetime.now(timezone.utc),))


def update_scenario(id, data):
    execute(UPDATE, (data["titre"], data["intention"], data["objectifs"], data["statut"], data["version"], data["referentiel_id"], data["auteur_id"], datetime.now(timezone.utc), id))


def delete_scenario(id):
    execute(DELETE, (id,))


def bulk_delete_scenarios(ids):
    """Supprime plusieurs enregistrements par ID. Aucune concaténation SQL."""
    if not ids:
        return
    placeholders = ", ".join("?" for _ in ids)
    execute("DELETE FROM scenario WHERE Id IN (" + placeholders + ")", list(ids))


_SEARCH_COLS  = ['scenario.Titre', 'scenario.Intention', 'scenario.Objectifs', 'scenario.Statut', 'scenario.Version']
_ALLOWED_SORT = {"titre": "scenario.Titre", "intention": "scenario.Intention", "objectifs": "scenario.Objectifs", "statut": "scenario.Statut", "version": "scenario.Version", "referentiel_id": "scenario.referentiel_id", "auteur_id": "scenario.auteur_id", "created_at": "scenario.CreatedAt", "updated_at": "scenario.UpdatedAt", "id": "scenario.Id"}
_ALLOWED_FILTERS = {"referentiel_id": "scenario.referentiel_id", "auteur_id": "scenario.auteur_id"}
_DEFAULT_SORT = "scenario.Id"


def count_scenarios(q: str | None = None, filters: dict[str, Any] | None = None) -> int:
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
        sql = "SELECT COUNT(*) AS total FROM scenario WHERE " + " AND ".join(clauses)
    else:
        sql = "SELECT COUNT(*) AS total FROM scenario"
    row = fetch_one(sql, params)
    return row["total"] if row else 0


def find_scenarios_paginated(q: str | None = None, sort: str | None = None, direction: str = "asc", limit: int = 10, offset: int = 0, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    sort_col = _ALLOWED_SORT.get(sort or "", _DEFAULT_SORT)
    sort_dir = "DESC" if direction == "desc" else "ASC"
    base = "SELECT scenario.*, referentiel_niveau_classe.Identifiant AS referentiel_id_label, professeur.Nom AS auteur_id_label FROM scenario LEFT JOIN referentiel_niveau_classe ON scenario.referentiel_id = referentiel_niveau_classe.Id LEFT JOIN professeur ON scenario.auteur_id = professeur.Id"
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


def find_scenarios_for_export(q: str | None = None, sort: str | None = None, direction: str = "asc", filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    return find_scenarios_paginated(
        q=q, sort=sort, direction=direction,
        limit=_EXPORT_LIMIT, offset=0, filters=filters,
    )



def get_referentiel_niveau_classe_choices():
    rows = fetch_all("SELECT Id, Identifiant FROM referentiel_niveau_classe ORDER BY Identifiant")
    return [(row["Id"], row["Identifiant"]) for row in rows]


def get_professeur_choices():
    rows = fetch_all("SELECT Id, Nom FROM professeur ORDER BY Nom")
    return [(row["Id"], row["Nom"]) for row in rows]


def get_competence_choices():
    rows = fetch_all("SELECT Id, Code FROM competence ORDER BY Code")
    return [(row["Id"], row["Code"]) for row in rows]


def get_critere_observable_choices():
    rows = fetch_all("SELECT Id, Libelle FROM critere_observable ORDER BY Libelle")
    return [(row["Id"], row["Libelle"]) for row in rows]


def get_scenario_competence_ids(id):
    rows = fetch_all("SELECT competence_id FROM scenario_competence WHERE scenario_id = ?", (id,))
    return [row["competence_id"] for row in rows]


def get_scenario_competence_labels_by_scenario_id(ids):
    if not ids:
        return {}
    placeholders = ", ".join("?" for _ in ids)
    rows = fetch_all(
        "SELECT pivot.scenario_id AS source_id, competence.Id AS target_id, competence.Code AS target_label "
        "FROM scenario_competence pivot "
        "JOIN competence ON competence.Id = pivot.competence_id "
        "WHERE pivot.scenario_id IN (" + placeholders + ") "
        "ORDER BY competence.Code",
        tuple(ids),
    )
    grouped = {}
    for row in rows:
        grouped.setdefault(row["source_id"], []).append(row["target_label"])
    return grouped


def get_scenario_competence_labels(id):
    rows = fetch_all(
        "SELECT competence.Id AS target_id, competence.Code AS target_label "
        "FROM scenario_competence pivot "
        "JOIN competence ON competence.Id = pivot.competence_id "
        "WHERE pivot.scenario_id = ? "
        "ORDER BY competence.Code",
        (id,),
    )
    return [row["target_label"] for row in rows]


def add_scenario_competence_ids(id, selected_ids):
    from core.database.transaction import transaction
    with transaction() as tx:
        for target_id in selected_ids:
            execute("INSERT INTO scenario_competence (scenario_id, competence_id) VALUES (?, ?)", (id, target_id), tx=tx)


def sync_scenario_competence_ids(id, selected_ids):
    from core.database.transaction import transaction
    with transaction() as tx:
        execute("DELETE FROM scenario_competence WHERE scenario_id = ?", (id,), tx=tx)
        for target_id in selected_ids:
            execute("INSERT INTO scenario_competence (scenario_id, competence_id) VALUES (?, ?)", (id, target_id), tx=tx)


def get_scenario_critere_observable_ids(id):
    rows = fetch_all("SELECT critere_observable_id FROM scenario_critere WHERE scenario_id = ?", (id,))
    return [row["critere_observable_id"] for row in rows]


def get_scenario_critere_observable_labels_by_scenario_id(ids):
    if not ids:
        return {}
    placeholders = ", ".join("?" for _ in ids)
    rows = fetch_all(
        "SELECT pivot.scenario_id AS source_id, critere_observable.Id AS target_id, critere_observable.Libelle AS target_label "
        "FROM scenario_critere pivot "
        "JOIN critere_observable ON critere_observable.Id = pivot.critere_observable_id "
        "WHERE pivot.scenario_id IN (" + placeholders + ") "
        "ORDER BY critere_observable.Libelle",
        tuple(ids),
    )
    grouped = {}
    for row in rows:
        grouped.setdefault(row["source_id"], []).append(row["target_label"])
    return grouped


def get_scenario_critere_observable_labels(id):
    rows = fetch_all(
        "SELECT critere_observable.Id AS target_id, critere_observable.Libelle AS target_label "
        "FROM scenario_critere pivot "
        "JOIN critere_observable ON critere_observable.Id = pivot.critere_observable_id "
        "WHERE pivot.scenario_id = ? "
        "ORDER BY critere_observable.Libelle",
        (id,),
    )
    return [row["target_label"] for row in rows]


def add_scenario_critere_observable_ids(id, selected_ids):
    from core.database.transaction import transaction
    with transaction() as tx:
        for target_id in selected_ids:
            execute("INSERT INTO scenario_critere (scenario_id, critere_observable_id) VALUES (?, ?)", (id, target_id), tx=tx)


def sync_scenario_critere_observable_ids(id, selected_ids):
    from core.database.transaction import transaction
    with transaction() as tx:
        execute("DELETE FROM scenario_critere WHERE scenario_id = ?", (id,), tx=tx)
        for target_id in selected_ids:
            execute("INSERT INTO scenario_critere (scenario_id, critere_observable_id) VALUES (?, ?)", (id, target_id), tx=tx)