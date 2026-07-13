# pyright: strict
"""Modèle de l'éditeur de scénario (ADR-019).

Lecture et écriture par section du scénario pédagogique (aligné cpro-education).
Phase 1 : section Titre (titre, co-intervention, co-auteurs). SQL visible et
paramétré. Les co-auteurs sont le many_to_many scenario <-> professeur
(pivot scenario_professeur).
"""
from typing import Any

from core.database.db import execute, fetch_all, fetch_one, insert
from core.database.transaction import transaction


def list_scenarios() -> list[dict[str, Any]]:
    """Tous les scénarios, les plus récemment modifiés d'abord."""
    return fetch_all(
        "SELECT s.Id, s.Titre, s.Statut, s.Version, s.CoIntervention, s.UpdatedAt, "
        "r.Identifiant AS referentiel_identifiant "
        "FROM scenario s LEFT JOIN referentiel_niveau_classe r ON r.Id = s.referentiel_id "
        "ORDER BY s.UpdatedAt DESC, s.Id DESC"
    )


def get_scenario(scenario_id: int) -> "dict[str, Any] | None":
    return fetch_one("SELECT * FROM scenario WHERE Id = ?", (scenario_id,))


def creer_scenario(titre: str) -> int:
    """Crée un scénario avec juste un titre ; le reste se remplit par sections (ADR-019)."""
    return insert(
        "INSERT INTO scenario (Titre, Intention, Statut, Version, CoIntervention, CreatedAt, UpdatedAt) "
        "VALUES (?, '', 'brouillon', '0.1.0', 0, NOW(), NOW())",
        (titre,),
    )


def list_professeurs() -> list[dict[str, Any]]:
    return fetch_all("SELECT Id, Nom, Prenom FROM professeur ORDER BY Nom, Prenom")


def get_co_auteur_ids(scenario_id: int) -> list[int]:
    rows = fetch_all(
        "SELECT professeur_id FROM scenario_professeur WHERE scenario_id = ?", (scenario_id,)
    )
    return [int(r["professeur_id"]) for r in rows]


def enregistrer_titre(
    scenario_id: int, titre: str, co_intervention: bool, co_auteur_ids: list[int]
) -> None:
    """Enregistre la section Titre : titre, co-intervention, et les co-auteurs (m2m)."""
    with transaction() as tx:
        execute(
            "UPDATE scenario SET Titre = ?, CoIntervention = ?, UpdatedAt = NOW() WHERE Id = ?",
            (titre, 1 if co_intervention else 0, scenario_id),
            tx=tx,
        )
        execute("DELETE FROM scenario_professeur WHERE scenario_id = ?", (scenario_id,), tx=tx)
        for pid in co_auteur_ids:
            execute(
                "INSERT INTO scenario_professeur (scenario_id, professeur_id) VALUES (?, ?)",
                (scenario_id, pid),
                tx=tx,
            )
