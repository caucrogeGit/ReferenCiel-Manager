# pyright: strict
"""Espace élève — « Mon parcours » (lecture seule).

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
    """Une ligne par parcours affecté à l'élève (titre, version, statut global)."""
    return fetch_all(
        "SELECT pe.Id AS progression_id, pe.Statut AS statut, "
        "p.Titre AS parcours_titre, vp.Version AS version "
        "FROM progression_eleve pe "
        "JOIN affectation_parcours ap ON ap.Id = pe.affectation_parcours_id "
        "JOIN version_parcours vp ON vp.Id = ap.version_parcours_id "
        "JOIN parcours p ON p.Id = vp.parcours_id "
        "WHERE pe.eleve_id = ? "
        "ORDER BY p.Titre, vp.Version",
        (eleve_id,),
    )


def paliers_progression(progression_id: int) -> list[dict[str, Any]]:
    """Les paliers d'une progression, dans l'ordre, avec leur statut."""
    return fetch_all(
        "SELECT pa.Ordre AS ordre, pa.Titre AS titre, pp.Statut AS statut "
        "FROM progression_palier pp "
        "JOIN palier pa ON pa.Id = pp.palier_id "
        "WHERE pp.progression_eleve_id = ? "
        "ORDER BY pa.Ordre",
        (progression_id,),
    )


def mon_parcours(user_id: int) -> dict[str, Any] | None:
    """Vue complète « Mon parcours » du compte : élève + parcours + paliers.

    Renvoie None si le compte n'est rattaché à aucun élève (compte élève non lié).
    """
    eleve = get_eleve_by_user(user_id)
    if eleve is None:
        return None
    progressions = mes_progressions(int(eleve["id"]))
    for prog in progressions:
        prog["paliers"] = paliers_progression(int(prog["progression_id"]))
    return {"eleve": eleve, "progressions": progressions}
