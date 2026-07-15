# pyright: strict
"""Bilan élève (ticket 21) : synthèse **arrêtée** des évaluations par critères.

Le bilan **fige** un instantané (champ `Synthese`, JSON sérialisé) au moment de sa
création : niveaux agrégés par compétence + détail des critères évalués. L'agrégation
remonte la chaîne d'évaluation de l'élève sur une progression :
`progression_palier → evaluation_activite → evaluation_critere → critere_observable →
competence`. SQL visible et paramétré (esprit Forge). Voir le
[dictionnaire](../../docs/specs/data-dictionary/dictionnaire-bilan.md).
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from core.database.db import fetch_all, fetch_one, insert

# Échelle ordinale des niveaux d'évaluation (`evaluation_critere.Niveau`).
_ORDRE = {"non_atteint": 0, "partiellement_atteint": 1, "atteint": 2, "depasse": 3}
_INVERSE = {0: "non_atteint", 1: "partiellement_atteint", 2: "atteint", 3: "depasse"}
_NON_EVALUE = "non_evalue"


def _niveau_agrege(niveaux: list[str]) -> str:
    """Niveau d'une compétence = moyenne ordinale arrondie de ses critères évalués.

    Une compétence sans critère évalué (liste vide, ou niveaux hors échelle) est
    marquée `non_evalue`.
    """
    valeurs = [_ORDRE[n] for n in niveaux if n in _ORDRE]
    if not valeurs:
        return _NON_EVALUE
    return _INVERSE[round(sum(valeurs) / len(valeurs))]


def lignes_evaluation(progression_parcours_id: int) -> list[dict[str, Any]]:
    """Évaluations de critères de l'élève sur la progression, avec leur compétence."""
    return fetch_all(
        "SELECT comp.Id AS competence_id, comp.Code AS competence_code, "
        "comp.Intitule AS competence_intitule, crit.Code AS critere_code, "
        "crit.Libelle AS critere_libelle, ec.Niveau AS niveau "
        "FROM progression_palier pp "
        "JOIN evaluation_activite ea ON ea.progression_palier_id = pp.Id "
        "JOIN evaluation_critere ec ON ec.evaluation_activite_id = ea.Id "
        "JOIN critere_observable crit ON crit.Id = ec.critere_id "
        "JOIN competence comp ON comp.Id = crit.competence_id "
        "WHERE pp.progression_parcours_id = ? "
        "ORDER BY comp.Code, crit.Code",
        (progression_parcours_id,),
    )


def agreger_synthese(progression_parcours_id: int) -> list[dict[str, Any]]:
    """Synthèse par compétence : niveau agrégé + détail des critères évalués.

    Les lignes arrivent déjà triées par code de compétence puis de critère ; on
    conserve cet ordre (dict ordonné par insertion).
    """
    par_competence: dict[int, dict[str, Any]] = {}
    for ligne in lignes_evaluation(progression_parcours_id):
        cid = int(ligne["competence_id"])
        comp = par_competence.setdefault(
            cid,
            {
                "competence_code": ligne["competence_code"],
                "competence_intitule": ligne["competence_intitule"],
                "criteres": [],
            },
        )
        comp["criteres"].append(
            {
                "critere_code": ligne["critere_code"],
                "critere_libelle": ligne["critere_libelle"],
                "niveau": ligne["niveau"],
            }
        )
    synthese: list[dict[str, Any]] = []
    for comp in par_competence.values():
        comp["niveau_agrege"] = _niveau_agrege([c["niveau"] for c in comp["criteres"]])
        synthese.append(comp)
    return synthese


def creer_bilan(
    *, progression_parcours_id: int, professeur_id: int, appreciation: str, statut: str
) -> int | None:
    """Crée un bilan en **figeant** la synthèse agrégée. Retourne l'id, ou None si la
    progression n'existe pas.

    L'`eleve_id` est **déduit** de la progression (cohérence : le bilan porte sur le
    parcours réellement suivi par cet élève).
    """
    prog = fetch_one(
        "SELECT eleve_id FROM progression_parcours WHERE Id = ?", (progression_parcours_id,)
    )
    if prog is None:
        return None
    eleve_id = int(prog["eleve_id"])
    synthese = json.dumps(agreger_synthese(progression_parcours_id), ensure_ascii=False)
    return insert(
        "INSERT INTO bilan_eleve (AppreciationGlobale, Statut, DateBilan, Synthese, "
        "eleve_id, professeur_id, progression_parcours_id, CreatedAt, UpdatedAt) "
        "VALUES (?, ?, NOW(), ?, ?, ?, ?, ?, ?)",
        (appreciation, statut, synthese, eleve_id, professeur_id, progression_parcours_id,
         datetime.now(timezone.utc), datetime.now(timezone.utc)),
    )


def get_bilan(bilan_id: int) -> dict[str, Any] | None:
    """Un bilan complet (élève, auteur, appréciation, synthèse **désérialisée**)."""
    row = fetch_one(
        "SELECT b.Id AS id, b.AppreciationGlobale AS appreciation, b.Statut AS statut, "
        "b.DateBilan AS date_bilan, b.Synthese AS synthese, "
        "e.Nom AS eleve_nom, e.Prenom AS eleve_prenom, "
        "p.Nom AS prof_nom, p.Prenom AS prof_prenom "
        "FROM bilan_eleve b "
        "JOIN eleve e ON e.Id = b.eleve_id "
        "JOIN professeur p ON p.Id = b.professeur_id "
        "WHERE b.Id = ?",
        (bilan_id,),
    )
    if row is not None and row.get("synthese"):
        row["synthese"] = json.loads(row["synthese"])
    return row


def list_bilans() -> list[dict[str, Any]]:
    """Liste des bilans (le plus récent d'abord), avec l'élève concerné."""
    return fetch_all(
        "SELECT b.Id AS id, b.Statut AS statut, b.DateBilan AS date_bilan, "
        "e.Nom AS eleve_nom, e.Prenom AS eleve_prenom "
        "FROM bilan_eleve b JOIN eleve e ON e.Id = b.eleve_id "
        "ORDER BY b.DateBilan DESC"
    )


def progressions_evaluables() -> list[dict[str, Any]]:
    """Progressions d'élèves (élève + parcours) candidates à un bilan — pour le formulaire."""
    return fetch_all(
        "SELECT pe.Id AS progression_id, e.Nom AS eleve_nom, e.Prenom AS eleve_prenom, "
        "p.Titre AS parcours_titre "
        "FROM progression_parcours pe "
        "JOIN eleve e ON e.Id = pe.eleve_id "
        "JOIN parcours p ON p.Id = pe.parcours_id "
        "ORDER BY e.Nom, e.Prenom"
    )
