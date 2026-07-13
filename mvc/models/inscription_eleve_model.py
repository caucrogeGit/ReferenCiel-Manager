from typing import Any

from core.database.db import fetch_one, fetch_all, execute, insert

SELECT_ALL   = "SELECT inscription_eleve.*, eleve.Nom AS eleve_id_label, classe.Libelle AS classe_id_label, annee_scolaire.Libelle AS annee_scolaire_id_label FROM inscription_eleve LEFT JOIN eleve ON inscription_eleve.eleve_id = eleve.Id LEFT JOIN classe ON inscription_eleve.classe_id = classe.Id LEFT JOIN annee_scolaire ON inscription_eleve.annee_scolaire_id = annee_scolaire.Id ORDER BY inscription_eleve.Id"
SELECT_BY_ID = "SELECT inscription_eleve.*, eleve.Nom AS eleve_id_label, classe.Libelle AS classe_id_label, annee_scolaire.Libelle AS annee_scolaire_id_label FROM inscription_eleve LEFT JOIN eleve ON inscription_eleve.eleve_id = eleve.Id LEFT JOIN classe ON inscription_eleve.classe_id = classe.Id LEFT JOIN annee_scolaire ON inscription_eleve.annee_scolaire_id = annee_scolaire.Id WHERE inscription_eleve.Id = ?"
INSERT       = "INSERT INTO inscription_eleve (DateInscription, eleve_id, classe_id, annee_scolaire_id) VALUES (?, ?, ?, ?)"
UPDATE       = "UPDATE inscription_eleve SET DateInscription = ?, eleve_id = ?, classe_id = ?, annee_scolaire_id = ? WHERE Id = ?"
DELETE       = "DELETE FROM inscription_eleve WHERE Id = ?"


def get_inscription_eleves():
    return fetch_all(SELECT_ALL)


def get_inscription_eleve_by_id(id):
    return fetch_one(SELECT_BY_ID, (id,))


def add_inscription_eleve(data):
    return insert(INSERT, (data["date_inscription"], data["eleve_id"], data["classe_id"], data["annee_scolaire_id"], ))


def update_inscription_eleve(id, data):
    execute(UPDATE, (data["date_inscription"], data["eleve_id"], data["classe_id"], data["annee_scolaire_id"], id))


def delete_inscription_eleve(id):
    execute(DELETE, (id,))


def bulk_delete_inscription_eleves(ids):
    """Supprime plusieurs enregistrements par ID. Aucune concaténation SQL."""
    if not ids:
        return
    placeholders = ", ".join("?" for _ in ids)
    execute("DELETE FROM inscription_eleve WHERE Id IN (" + placeholders + ")", list(ids))


_SEARCH_COLS  = []
_ALLOWED_SORT = {"date_inscription": "inscription_eleve.DateInscription", "eleve_id": "inscription_eleve.eleve_id", "classe_id": "inscription_eleve.classe_id", "annee_scolaire_id": "inscription_eleve.annee_scolaire_id", "created_at": "inscription_eleve.CreatedAt", "updated_at": "inscription_eleve.UpdatedAt", "id": "inscription_eleve.Id"}
_ALLOWED_FILTERS = {"eleve_id": "inscription_eleve.eleve_id", "classe_id": "inscription_eleve.classe_id", "annee_scolaire_id": "inscription_eleve.annee_scolaire_id"}
_DEFAULT_SORT = "inscription_eleve.Id"


def count_inscription_eleves(q: str | None = None, filters: dict[str, Any] | None = None) -> int:
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
        sql = "SELECT COUNT(*) AS total FROM inscription_eleve WHERE " + " AND ".join(clauses)
    else:
        sql = "SELECT COUNT(*) AS total FROM inscription_eleve"
    row = fetch_one(sql, params)
    return row["total"] if row else 0


def find_inscription_eleves_paginated(q: str | None = None, sort: str | None = None, direction: str = "asc", limit: int = 10, offset: int = 0, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    sort_col = _ALLOWED_SORT.get(sort or "", _DEFAULT_SORT)
    sort_dir = "DESC" if direction == "desc" else "ASC"
    base = "SELECT inscription_eleve.*, eleve.Nom AS eleve_id_label, classe.Libelle AS classe_id_label, annee_scolaire.Libelle AS annee_scolaire_id_label FROM inscription_eleve LEFT JOIN eleve ON inscription_eleve.eleve_id = eleve.Id LEFT JOIN classe ON inscription_eleve.classe_id = classe.Id LEFT JOIN annee_scolaire ON inscription_eleve.annee_scolaire_id = annee_scolaire.Id"
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


def find_inscription_eleves_for_export(q: str | None = None, sort: str | None = None, direction: str = "asc", filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    return find_inscription_eleves_paginated(
        q=q, sort=sort, direction=direction,
        limit=_EXPORT_LIMIT, offset=0, filters=filters,
    )



def get_eleve_choices():
    rows = fetch_all("SELECT Id, Nom FROM eleve ORDER BY Nom")
    return [(row["Id"], row["Nom"]) for row in rows]


def get_classe_choices():
    rows = fetch_all("SELECT Id, Libelle FROM classe ORDER BY Libelle")
    return [(row["Id"], row["Libelle"]) for row in rows]


def get_annee_scolaire_choices():
    rows = fetch_all("SELECT Id, Libelle FROM annee_scolaire ORDER BY Libelle")
    return [(row["Id"], row["Libelle"]) for row in rows]