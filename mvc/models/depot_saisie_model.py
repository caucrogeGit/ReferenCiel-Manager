# pyright: strict
"""Espace élève v2 — déposer un fichier pour l'activité d'une séance (appartenance).

L'élève dépose un fichier rattaché à l'activité de l'un de **ses** seances ; le
fichier est stocké par l'opt-in `files` (allowlist + taille), et le dépôt
enregistré (`depot_eleve`). L'**évaluation** reste au professeur : déposer ne
change pas le statut de la séance. Sécurité row-level vérifiée à chaque appel.
"""
from __future__ import annotations

from typing import Any

from core.database.db import fetch_all, fetch_one, insert


def _seance_de_l_eleve(progression_palier_id: int, user_id: int) -> dict[str, Any] | None:
    return fetch_one(
        "SELECT pp.Id AS progression_palier_id, pp.seance_id AS seance_id, pa.Titre AS seance_titre "
        "FROM progression_palier pp "
        "JOIN progression_parcours pe ON pe.Id = pp.progression_parcours_id "
        "JOIN eleve e ON e.Id = pe.eleve_id "
        "JOIN seance pa ON pa.Id = pp.seance_id "
        "WHERE pp.Id = ? AND e.UserId = ?",
        (progression_palier_id, user_id),
    )


def _activite_du_seance(seance_id: int) -> dict[str, Any] | None:
    return fetch_one(
        "SELECT Id AS id, Fichier AS consigne FROM activite WHERE seance_id = ? ORDER BY Id LIMIT 1",
        (seance_id,),
    )


def get_activite_depots(progression_palier_id: int, user_id: int) -> dict[str, Any] | None:
    """Activité de la séance + dépôts déjà remis par l'élève, si la séance lui appartient."""
    seance = _seance_de_l_eleve(progression_palier_id, user_id)
    if seance is None:
        return None
    activite = _activite_du_seance(int(seance["seance_id"]))
    if activite is None:
        return None
    depots = fetch_all(
        "SELECT Id AS id, Fichier AS fichier, DateDepot AS date_depot "
        "FROM depot_eleve WHERE progression_palier_id = ? AND activite_id = ? "
        "ORDER BY DateDepot DESC",
        (progression_palier_id, activite["id"]),
    )
    return {
        "progression_palier_id": progression_palier_id,
        "seance_titre": seance["seance_titre"],
        "activite_id": activite["id"],
        "consigne": activite["consigne"],
        "depots": depots,
    }


def enregistrer_depot(
    progression_palier_id: int, user_id: int, fichier_path: str
) -> dict[str, Any] | None:
    """Enregistre un dépôt (fichier déjà stocké) pour l'activité de la séance.

    Renvoie {depot_id, activite_id} ou None si la séance n'appartient pas au compte
    ou n'a pas d'activité.
    """
    seance = _seance_de_l_eleve(progression_palier_id, user_id)
    if seance is None:
        return None
    activite = _activite_du_seance(int(seance["seance_id"]))
    if activite is None:
        return None
    depot_id = insert(
        "INSERT INTO depot_eleve "
        "(Fichier, DateDepot, progression_palier_id, activite_id, CreatedAt, UpdatedAt) "
        "VALUES (?, NOW(), ?, ?, NOW(), NOW())",
        (fichier_path, progression_palier_id, activite["id"]),
    )
    return {"depot_id": depot_id, "activite_id": int(activite["id"])}
