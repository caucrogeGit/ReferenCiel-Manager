# pyright: strict
"""Espace élève — « Mon sequence » (lecture seule).

Vues de synthèse sur la progression de l'élève **connecté**, filtrées par son
compte (`eleve.UserId = ?`) : c'est la sécurité au niveau **ligne** (row-level),
l'élève ne voit que ses propres données. SQL visible et paramétré (esprit Forge).
Aucune écriture : le premier incrément de l'espace élève est en consultation.
"""
from __future__ import annotations

from typing import Any

from core.database.db import fetch_all, fetch_one


def get_eleve_by_user(user_id: int) -> dict[str, Any] | None:
    """L'élève rattaché à ce compte, ou None si le compte n'est lié à aucun élève."""
    return fetch_one(
        "SELECT Id AS id, Nom AS nom, Prenom AS prenom FROM eleve WHERE UserId = ?",
        (user_id,),
    )


def mes_progressions(eleve_id: int) -> list[dict[str, Any]]:
    """Une ligne par séquence affectée à l'élève (titre, version, statut global)."""
    return fetch_all(
        "SELECT pe.Id AS progression_id, pe.Statut AS statut, "
        "p.Titre AS sequence_titre, p.Identifiant AS sequence_identifiant "
        "FROM progression_sequence pe "
        "JOIN sequence p ON p.Id = pe.sequence_id "
        "WHERE pe.eleve_id = ? "
        "ORDER BY p.Titre",
        (eleve_id,),
    )


def seances_progression(progression_id: int) -> list[dict[str, Any]]:
    """Les seances d'une progression, dans l'ordre, avec leur statut.

    Expose `progression_seance_id` (cible des actions de saisie) et `qcm_id`
    (présence d'un QCM à passer, ou NULL) pour la vue « Mon sequence ».
    """
    return fetch_all(
        "SELECT pp.Id AS progression_seance_id, pa.Ordre AS ordre, pa.Titre AS titre, "
        "pp.Statut AS statut, "
        "(SELECT MIN(Id) FROM qcm WHERE seance_id = pa.Id) AS qcm_id, "
        "(SELECT MIN(Id) FROM checklist WHERE seance_id = pa.Id) AS checklist_id, "
        "(SELECT MIN(Id) FROM activite WHERE seance_id = pa.Id) AS activite_id "
        "FROM progression_seance pp "
        "JOIN seance pa ON pa.Id = pp.seance_id "
        "WHERE pp.progression_sequence_id = ? "
        "ORDER BY pa.Ordre",
        (progression_id,),
    )


def mon_parcours(user_id: int) -> dict[str, Any] | None:
    """Vue complète « Mon sequence » du compte : élève + sequence + seances.

    Renvoie None si le compte n'est rattaché à aucun élève (compte élève non lié).
    """
    eleve = get_eleve_by_user(user_id)
    if eleve is None:
        return None
    progressions = mes_progressions(int(eleve["id"]))
    for prog in progressions:
        prog["seances"] = seances_progression(int(prog["progression_id"]))
    return {"eleve": eleve, "progressions": progressions}
