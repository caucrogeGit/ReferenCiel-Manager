# pyright: strict
"""Suivi professeur (ticket 20) : requêtes d'agrégation en **lecture seule** sur la
progression des élèves. Pas de nouvelle entité — des vues de synthèse sur les tables
existantes (affectation, progression, palier), SQL visible et paramétré (esprit Forge).
"""
from __future__ import annotations

from typing import Any

from core.database.db import fetch_all, fetch_one

_STATUT_PALIER_VALIDE = "valide"
_STATUT_PALIER_BLOQUE = "bloque"
_STATUT_PALIER_EN_COURS = "en_cours"


def list_affectations() -> list[dict[str, Any]]:
    """Affectations avec leur classe et le nombre d'élèves suivis (progressions)."""
    return fetch_all(
        "SELECT ap.Id AS id, ap.DateAffectation AS date_affectation, ap.Statut AS statut, "
        "c.Code AS classe_code, c.Libelle AS classe_libelle, "
        "COUNT(DISTINCT pe.Id) AS nb_progressions "
        "FROM affectation_parcours ap "
        "JOIN classe c ON c.Id = ap.classe_id "
        "LEFT JOIN progression_parcours pe ON pe.affectation_parcours_id = ap.Id "
        "GROUP BY ap.Id, ap.DateAffectation, ap.Statut, c.Code, c.Libelle "
        "ORDER BY ap.DateAffectation DESC"
    )


def get_affectation(affectation_id: int) -> dict[str, Any] | None:
    """En-tête d'une affectation (classe + statut) pour la page de détail."""
    return fetch_one(
        "SELECT ap.Id AS id, ap.DateAffectation AS date_affectation, ap.Statut AS statut, "
        "c.Code AS classe_code, c.Libelle AS classe_libelle "
        "FROM affectation_parcours ap "
        "JOIN classe c ON c.Id = ap.classe_id "
        "WHERE ap.Id = ?",
        (affectation_id,),
    )


def suivi_eleves(affectation_id: int) -> list[dict[str, Any]]:
    """Pour une affectation : un élève par ligne, avec l'avancement par palier agrégé
    (validés / en cours / bloqués / total) — de quoi repérer les élèves bloqués."""
    return fetch_all(
        "SELECT pe.Id AS progression_id, e.Nom AS nom, e.Prenom AS prenom, "
        "pe.Statut AS statut, "
        "SUM(pp.Statut = ?) AS nb_valide, "
        "SUM(pp.Statut = ?) AS nb_bloque, "
        "SUM(pp.Statut = ?) AS nb_en_cours, "
        "COUNT(pp.Id) AS nb_paliers "
        "FROM progression_parcours pe "
        "JOIN eleve e ON e.Id = pe.eleve_id "
        "LEFT JOIN progression_palier pp ON pp.progression_parcours_id = pe.Id "
        "WHERE pe.affectation_parcours_id = ? "
        "GROUP BY pe.Id, e.Nom, e.Prenom, pe.Statut "
        "ORDER BY e.Nom, e.Prenom",
        (_STATUT_PALIER_VALIDE, _STATUT_PALIER_BLOQUE, _STATUT_PALIER_EN_COURS, affectation_id),
    )
