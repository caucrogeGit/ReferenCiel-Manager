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
        "LEFT JOIN progression_sequence pe ON pe.eleve_id = e.Id "
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


# Cycle de vie d'une séance côté élève (ADR-032/033). « En attente de validation »
# = ce que le professeur a à traiter.
_STATUT_ATTENTE = "en_attente_validation"
STATUT_SEANCE_LABELS = {
    "non_commencee": "Non commencée",
    "en_cours": "En cours",
    "en_attente_validation": "En attente de validation",
    "a_reprendre": "À reprendre",
    "validee": "Validée",
}


def compter_lentilles(professeur_id: int) -> dict[str, int]:
    """Compteurs pour les tuiles (classes / séquences suivies / séances à évaluer)."""
    row = fetch_one(
        "SELECT COUNT(DISTINCT c.Id) AS nb_classes, COUNT(DISTINCT pe.sequence_id) AS nb_sequences, "
        "COALESCE(SUM(pp.Statut = ?), 0) AS nb_a_evaluer "
        "FROM classe_professeur cp "
        "JOIN classe c ON c.Id = cp.classe_id "
        "LEFT JOIN eleve e ON e.classe_id = c.Id "
        "LEFT JOIN progression_sequence pe ON pe.eleve_id = e.Id "
        "LEFT JOIN progression_seance pp ON pp.progression_sequence_id = pe.Id "
        "WHERE cp.professeur_id = ?",
        (_STATUT_ATTENTE, professeur_id),
    )
    return {
        "nb_classes": int(row["nb_classes"]) if row else 0,
        "nb_sequences": int(row["nb_sequences"]) if row else 0,
        "nb_a_evaluer": int(row["nb_a_evaluer"]) if row else 0,
    }


def list_seances_a_evaluer(professeur_id: int) -> list[dict[str, Any]]:
    """Séances où les élèves du prof ont une progression, avec le compte par statut.
    Triées par « en attente de validation » d'abord — la file de travail (ADR-033)."""
    return fetch_all(
        "SELECT se.Id AS id, se.Titre AS seance_titre, sq.Titre AS sequence_titre, "
        "COALESCE(SUM(pp.Statut = 'en_attente_validation'), 0) AS nb_attente, "
        "COALESCE(SUM(pp.Statut = 'a_reprendre'), 0) AS nb_a_reprendre, "
        "COALESCE(SUM(pp.Statut = 'en_cours'), 0) AS nb_en_cours, "
        "COALESCE(SUM(pp.Statut = 'validee'), 0) AS nb_validee, "
        "COUNT(pp.Id) AS nb_total "
        "FROM classe_professeur cp "
        "JOIN classe c ON c.Id = cp.classe_id "
        "JOIN eleve e ON e.classe_id = c.Id "
        "JOIN progression_sequence pe ON pe.eleve_id = e.Id "
        "JOIN progression_seance pp ON pp.progression_sequence_id = pe.Id "
        "JOIN seance se ON se.Id = pp.seance_id "
        "JOIN sequence sq ON sq.Id = se.sequence_id "
        "WHERE cp.professeur_id = ? "
        "GROUP BY se.Id, se.Titre, sq.Titre "
        "ORDER BY nb_attente DESC, se.Titre",
        (professeur_id,),
    )


def get_seance_suivi(seance_id: int) -> dict[str, Any] | None:
    """En-tête d'une séance (titre + séquence) pour la lentille « séance »."""
    return fetch_one(
        "SELECT se.Id AS id, se.Titre AS seance_titre, sq.Titre AS sequence_titre "
        "FROM seance se JOIN sequence sq ON sq.Id = se.sequence_id WHERE se.Id = ?",
        (seance_id,),
    )


def eleves_pour_seance(seance_id: int, professeur_id: int) -> list[dict[str, Any]]:
    """Élèves du prof concernés par une séance, avec leur statut (pour l'évaluation)."""
    return fetch_all(
        "SELECT pp.Id AS progression_seance_id, pe.Id AS progression_id, "
        "e.Nom AS nom, e.Prenom AS prenom, c.Code AS classe_code, pp.Statut AS statut "
        "FROM classe_professeur cp "
        "JOIN classe c ON c.Id = cp.classe_id "
        "JOIN eleve e ON e.classe_id = c.Id "
        "JOIN progression_sequence pe ON pe.eleve_id = e.Id "
        "JOIN progression_seance pp ON pp.progression_sequence_id = pe.Id AND pp.seance_id = ? "
        "WHERE cp.professeur_id = ? "
        "ORDER BY pp.Statut, e.Nom, e.Prenom",
        (seance_id, professeur_id),
    )


def list_sequences(professeur_id: int) -> list[dict[str, Any]]:
    """Séquences suivies (une progression existe chez un élève du prof), avec le
    nombre de classes, d'élèves et de progressions concernés — lentille « séquence »."""
    return fetch_all(
        "SELECT p.Id AS id, p.Titre AS sequence_titre, "
        "COUNT(DISTINCT c.Id) AS nb_classes, "
        "COUNT(DISTINCT e.Id) AS nb_eleves, "
        "COUNT(DISTINCT pe.Id) AS nb_progressions "
        "FROM classe_professeur cp "
        "JOIN classe c ON c.Id = cp.classe_id "
        "JOIN eleve e ON e.classe_id = c.Id "
        "JOIN progression_sequence pe ON pe.eleve_id = e.Id "
        "JOIN sequence p ON p.Id = pe.sequence_id "
        "WHERE cp.professeur_id = ? "
        "GROUP BY p.Id, p.Titre "
        "ORDER BY p.Titre",
        (professeur_id,),
    )


def get_sequence_suivi(sequence_id: int) -> dict[str, Any] | None:
    """En-tête d'une séquence pour la lentille « séquence »."""
    return fetch_one(
        "SELECT Id AS id, Titre AS sequence_titre FROM sequence WHERE Id = ?", (sequence_id,)
    )


def classes_pour_sequence(sequence_id: int, professeur_id: int) -> list[dict[str, Any]]:
    """Classes du professeur qui utilisent une séquence (progressions existantes)."""
    return fetch_all(
        "SELECT c.Id AS id, c.Code AS classe_code, c.Libelle AS classe_libelle, "
        "COUNT(DISTINCT e.Id) AS nb_eleves, "
        "COUNT(DISTINCT pe.Id) AS nb_progressions "
        "FROM classe_professeur cp "
        "JOIN classe c ON c.Id = cp.classe_id "
        "JOIN eleve e ON e.classe_id = c.Id "
        "JOIN progression_sequence pe ON pe.eleve_id = e.Id AND pe.sequence_id = ? "
        "WHERE cp.professeur_id = ? "
        "GROUP BY c.Id, c.Code, c.Libelle "
        "ORDER BY c.Code",
        (sequence_id, professeur_id),
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
        "JOIN progression_sequence pe ON pe.eleve_id = e.Id "
        "JOIN sequence p ON p.Id = pe.sequence_id "
        "LEFT JOIN progression_seance pp ON pp.progression_sequence_id = pe.Id "
        "WHERE e.classe_id = ? "
        "GROUP BY pe.Id, e.Nom, e.Prenom, p.Titre, pe.Statut "
        "ORDER BY e.Nom, e.Prenom, p.Titre",
        (_STATUT_SEANCE_VALIDE, _STATUT_SEANCE_BLOQUE, _STATUT_SEANCE_EN_COURS, classe_id),
    )
