from typing import Any

from core.database.db import fetch_one, fetch_all, execute, insert

SELECT_ALL   = "SELECT affectation_professeur_classe.*, professeur.Nom AS professeur_id_label, classe.Libelle AS classe_id_label, annee_scolaire.Libelle AS annee_scolaire_id_label FROM affectation_professeur_classe LEFT JOIN professeur ON affectation_professeur_classe.professeur_id = professeur.Id LEFT JOIN classe ON affectation_professeur_classe.classe_id = classe.Id LEFT JOIN annee_scolaire ON affectation_professeur_classe.annee_scolaire_id = annee_scolaire.Id ORDER BY affectation_professeur_classe.Id"
SELECT_BY_ID = "SELECT affectation_professeur_classe.*, professeur.Nom AS professeur_id_label, classe.Libelle AS classe_id_label, annee_scolaire.Libelle AS annee_scolaire_id_label FROM affectation_professeur_classe LEFT JOIN professeur ON affectation_professeur_classe.professeur_id = professeur.Id LEFT JOIN classe ON affectation_professeur_classe.classe_id = classe.Id LEFT JOIN annee_scolaire ON affectation_professeur_classe.annee_scolaire_id = annee_scolaire.Id WHERE affectation_professeur_classe.Id = ?"
INSERT       = "INSERT INTO affectation_professeur_classe (Role, professeur_id, classe_id, annee_scolaire_id, CreatedAt, UpdatedAt) VALUES (?, ?, ?, ?, ?, ?)"
UPDATE       = "UPDATE affectation_professeur_classe SET Role = ?, professeur_id = ?, classe_id = ?, annee_scolaire_id = ?, CreatedAt = ?, UpdatedAt = ? WHERE Id = ?"
DELETE       = "DELETE FROM affectation_professeur_classe WHERE Id = ?"


def get_affectation_professeur_classes():
    return fetch_all(SELECT_ALL)


def get_affectation_professeur_classe_by_id(id):
    return fetch_one(SELECT_BY_ID, (id,))


def add_affectation_professeur_classe(data):
    return insert(INSERT, (data["role"], data["professeur_id"], data["classe_id"], data["annee_scolaire_id"], data["created_at"], data["updated_at"],))


def update_affectation_professeur_classe(id, data):
    execute(UPDATE, (data["role"], data["professeur_id"], data["classe_id"], data["annee_scolaire_id"], data["created_at"], data["updated_at"], id))


def delete_affectation_professeur_classe(id):
    execute(DELETE, (id,))


def bulk_delete_affectation_professeur_classes(ids):
    """Supprime plusieurs enregistrements par ID. Aucune concaténation SQL."""
    if not ids:
        return
    placeholders = ", ".join("?" for _ in ids)
    execute("DELETE FROM affectation_professeur_classe WHERE Id IN (" + placeholders + ")", list(ids))


_SEARCH_COLS  = ['affectation_professeur_classe.Role']
_ALLOWED_SORT = {"role": "affectation_professeur_classe.Role", "professeur_id": "affectation_professeur_classe.professeur_id", "classe_id": "affectation_professeur_classe.classe_id", "annee_scolaire_id": "affectation_professeur_classe.annee_scolaire_id", "created_at": "affectation_professeur_classe.CreatedAt", "updated_at": "affectation_professeur_classe.UpdatedAt", "id": "affectation_professeur_classe.Id"}
_ALLOWED_FILTERS = {"professeur_id": "affectation_professeur_classe.professeur_id", "classe_id": "affectation_professeur_classe.classe_id", "annee_scolaire_id": "affectation_professeur_classe.annee_scolaire_id"}
_DEFAULT_SORT = "affectation_professeur_classe.Id"


def count_affectation_professeur_classes(q: str | None = None, filters: dict[str, Any] | None = None) -> int:
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
        sql = "SELECT COUNT(*) AS total FROM affectation_professeur_classe WHERE " + " AND ".join(clauses)
    else:
        sql = "SELECT COUNT(*) AS total FROM affectation_professeur_classe"
    row = fetch_one(sql, params)
    return row["total"] if row else 0


def find_affectation_professeur_classes_paginated(q: str | None = None, sort: str | None = None, direction: str = "asc", limit: int = 10, offset: int = 0, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    sort_col = _ALLOWED_SORT.get(sort or "", _DEFAULT_SORT)
    sort_dir = "DESC" if direction == "desc" else "ASC"
    base = "SELECT affectation_professeur_classe.*, professeur.Nom AS professeur_id_label, classe.Libelle AS classe_id_label, annee_scolaire.Libelle AS annee_scolaire_id_label FROM affectation_professeur_classe LEFT JOIN professeur ON affectation_professeur_classe.professeur_id = professeur.Id LEFT JOIN classe ON affectation_professeur_classe.classe_id = classe.Id LEFT JOIN annee_scolaire ON affectation_professeur_classe.annee_scolaire_id = annee_scolaire.Id"
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


def find_affectation_professeur_classes_for_export(q: str | None = None, sort: str | None = None, direction: str = "asc", filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    return find_affectation_professeur_classes_paginated(
        q=q, sort=sort, direction=direction,
        limit=_EXPORT_LIMIT, offset=0, filters=filters,
    )



def get_professeur_choices():
    rows = fetch_all("SELECT Id, Nom FROM professeur ORDER BY Nom")
    return [(row["Id"], row["Nom"]) for row in rows]


def get_classe_choices():
    rows = fetch_all("SELECT Id, Libelle FROM classe ORDER BY Libelle")
    return [(row["Id"], row["Libelle"]) for row in rows]


def get_annee_scolaire_choices():
    rows = fetch_all("SELECT Id, Libelle FROM annee_scolaire ORDER BY Libelle")
    return [(row["Id"], row["Libelle"]) for row in rows]