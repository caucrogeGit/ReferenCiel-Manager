# pyright: strict
"""Suivi professeur (ticket 20, revu ADR-022) : requêtes d'agrégation en **lecture
seule** sur la progression des élèves, organisées **par CLASSE du professeur**.

Le professeur voit ses classes (pivot `classe_professeur`) ; pour une classe, ses
élèves (`eleve.classe_id`) et l'avancement de chacun sur ses sequence (une ligne
par progression). Pas de nouvelle entité — vues de synthèse, SQL visible et
paramétré (esprit Forge).
"""
from __future__ import annotations

from typing import Any

from core.database.db import fetch_all, fetch_one

_STATUT_SEANCE_VALIDE = "valide"
_STATUT_SEANCE_BLOQUE = "bloque"
_STATUT_SEANCE_EN_COURS = "en_cours"


def list_classes(professeur_id: int) -> list[dict[str, Any]]:
    """Les classes du professeur, avec le nombre d'élèves et de progressions suivies."""
    return fetch_all(
        "SELECT c.Id AS id, c.Code AS classe_code, c.Libelle AS classe_libelle, "
        "nc.Code AS niveau_code, asc2.Libelle AS annee_libelle, "
        "COUNT(DISTINCT e.Id) AS nb_eleves, "
        "COUNT(DISTINCT pe.Id) AS nb_progressions "
        "FROM classe_professeur cp "
        "JOIN classe c ON c.Id = cp.classe_id "
        "JOIN formation_niveau fn ON fn.Id = c.formation_niveau_id "
        "JOIN niveau_classe nc ON nc.Id = fn.niveau_classe_id "
        "JOIN annee_scolaire asc2 ON asc2.Id = c.annee_scolaire_id "
        "LEFT JOIN eleve e ON e.classe_id = c.Id "
        "LEFT JOIN progression_parcours pe ON pe.eleve_id = e.Id "
        "WHERE cp.professeur_id = ? "
        "GROUP BY c.Id, c.Code, c.Libelle, nc.Code, asc2.Libelle "
        "ORDER BY asc2.Libelle DESC, nc.Code, c.Code",
        (professeur_id,),
    )


def get_classe(classe_id: int) -> dict[str, Any] | None:
    """En-tête d'une classe (code + niveau + année) pour la page de détail."""
    return fetch_one(
        "SELECT c.Id AS id, c.Code AS classe_code, c.Libelle AS classe_libelle, "
        "nc.Code AS niveau_code, asc2.Libelle AS annee_libelle "
        "FROM classe c "
        "JOIN formation_niveau fn ON fn.Id = c.formation_niveau_id "
        "JOIN niveau_classe nc ON nc.Id = fn.niveau_classe_id "
        "JOIN annee_scolaire asc2 ON asc2.Id = c.annee_scolaire_id "
        "WHERE c.Id = ?",
        (classe_id,),
    )


def suivi_eleves(classe_id: int) -> list[dict[str, Any]]:
    """Pour une classe : une ligne par progression d'élève (élève + sequence), avec
    l'avancement par seance agrégé (validés / en cours / bloqués / total) — de quoi
    repérer les élèves bloqués."""
    return fetch_all(
        "SELECT pe.Id AS progression_id, e.Nom AS nom, e.Prenom AS prenom, "
        "p.Titre AS sequence_titre, pe.Statut AS statut, "
        "SUM(pp.Statut = ?) AS nb_valide, "
        "SUM(pp.Statut = ?) AS nb_bloque, "
        "SUM(pp.Statut = ?) AS nb_en_cours, "
        "COUNT(pp.Id) AS nb_seances "
        "FROM eleve e "
        "JOIN progression_parcours pe ON pe.eleve_id = e.Id "
        "JOIN sequence p ON p.Id = pe.sequence_id "
        "LEFT JOIN progression_seance pp ON pp.progression_parcours_id = pe.Id "
        "WHERE e.classe_id = ? "
        "GROUP BY pe.Id, e.Nom, e.Prenom, p.Titre, pe.Statut "
        "ORDER BY e.Nom, e.Prenom, p.Titre",
        (_STATUT_SEANCE_VALIDE, _STATUT_SEANCE_BLOQUE, _STATUT_SEANCE_EN_COURS, classe_id),
    )
