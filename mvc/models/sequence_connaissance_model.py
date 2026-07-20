"""Lien Séquence ↔ Connaissance (ADR-028).

Une séquence retient des connaissances du référentiel de son scénario appairé,
et leur attribue un niveau cible (distinct du niveau officiel) et un statut dans
la progression. Écriture ciblée d'un seul lien par requête, comme les pivots du
tunnel scénario (évite les races entre requêtes HTMX concurrentes).
"""

from datetime import datetime, timezone
from typing import Any

from core.database.db import fetch_all, fetch_one, execute, insert

# Statuts autorisés (ADR-028). L'ordre reflète la progression pédagogique.
STATUTS = ("prerequis", "apportee", "mobilisee", "consolidee")
STATUT_LABELS = {
    "prerequis": "Prérequis",
    "apportee": "Apportée",
    "mobilisee": "Mobilisée",
    "consolidee": "Consolidée",
}

# Niveaux taxonomiques officiels du référentiel (Bac Pro CIEL). Le niveau 4
# n'est pas utilisé en Bac Pro (objectif méthodologique de niveau supérieur).
NIVEAUX_TAXONOMIE = {
    1: "Information",
    2: "Expression",
    3: "Maîtrise d'outils",
    4: "Maîtrise méthodologique",
}


def get_referentiel_id_for_sequence(sequence_id):
    """Référentiel de la séquence, via son scénario appairé. None si aucun."""
    row = fetch_one(
        "SELECT s.referentiel_id AS ref "
        "FROM scenario_sequence ss JOIN scenario s ON s.Id = ss.scenario_id "
        "WHERE ss.sequence_id = ? LIMIT 1",
        (sequence_id,),
    )
    return row["ref"] if row and row["ref"] is not None else None


def get_scenario_id_for_sequence(sequence_id):
    """Scénario appairé à la séquence (1-1, ADR-029). None si aucun."""
    row = fetch_one(
        "SELECT scenario_id FROM scenario_sequence WHERE sequence_id = ? LIMIT 1",
        (sequence_id,),
    )
    return row["scenario_id"] if row else None


def get_arbre_connaissances(ref_id):
    """Compétences du référentiel, chacune avec ses connaissances (niveau officiel)."""
    competences = fetch_all(
        "SELECT Id, Code, Intitule FROM competence WHERE referentiel_id = ? ORDER BY Code",
        (ref_id,),
    )
    connaissances = fetch_all(
        "SELECT k.Id, k.Libelle, k.NiveauTaxonomique, k.competence_id "
        "FROM connaissance k JOIN competence cp ON cp.Id = k.competence_id "
        "WHERE cp.referentiel_id = ? ORDER BY k.competence_id, k.Id",
        (ref_id,),
    )
    par_comp = {}
    for k in connaissances:
        par_comp.setdefault(k["competence_id"], []).append(k)
    for comp in competences:
        comp["connaissances"] = par_comp.get(comp["Id"], [])
    return competences


def get_sequence_id_for_scenario(scenario_id: int) -> "int | None":
    """Séquence appairée à un scénario (1-1). None si aucune."""
    row = fetch_one(
        "SELECT sequence_id FROM scenario_sequence WHERE scenario_id = ? LIMIT 1",
        (scenario_id,),
    )
    return row["sequence_id"] if row else None


def get_connaissances_retenues(sequence_id: int, ref_id: int) -> "list[dict[str, Any]]":
    """Connaissances retenues par la séquence, groupées par compétence.

    Structure d'export commune (PDF, Markdown, JSON) : liste de compétences,
    chacune avec ses connaissances retenues (niveau officiel + cible + statut).
    Les compétences sans connaissance retenue sont omises.
    """
    liens = get_liens_by_sequence(sequence_id)
    groupes = []
    for comp in get_arbre_connaissances(ref_id):
        retenues = []
        for k in comp["connaissances"]:
            lien = liens.get(k["Id"])
            if lien is None:
                continue
            statut = lien["Statut"]
            retenues.append({
                "libelle": k["Libelle"],
                "niveau_officiel": k["NiveauTaxonomique"],
                "niveau_cible": lien["NiveauCible"],
                "statut": statut,
                "statut_label": STATUT_LABELS.get(statut) if statut else None,
            })
        if retenues:
            groupes.append({
                "code": comp["Code"],
                "intitule": comp["Intitule"],
                "connaissances": retenues,
            })
    return groupes


def get_liens_by_sequence(sequence_id):
    """Liens de la séquence, indexés par connaissance_id."""
    rows = fetch_all(
        "SELECT connaissance_id, NiveauCible, Statut, Commentaire "
        "FROM sequence_connaissance WHERE sequence_id = ?",
        (sequence_id,),
    )
    return {row["connaissance_id"]: row for row in rows}


def _lien_existe(sequence_id, connaissance_id):
    return fetch_one(
        "SELECT Id FROM sequence_connaissance WHERE sequence_id = ? AND connaissance_id = ?",
        (sequence_id, connaissance_id),
    ) is not None


def lier(sequence_id, connaissance_id):
    """Retient une connaissance (niveau cible et statut non renseignés au départ)."""
    if _lien_existe(sequence_id, connaissance_id):
        return
    now = datetime.now(timezone.utc)
    insert(
        "INSERT INTO sequence_connaissance "
        "(sequence_id, connaissance_id, CreatedAt, UpdatedAt) VALUES (?, ?, ?, ?)",
        (sequence_id, connaissance_id, now, now),
    )


def delier(sequence_id, connaissance_id):
    execute(
        "DELETE FROM sequence_connaissance WHERE sequence_id = ? AND connaissance_id = ?",
        (sequence_id, connaissance_id),
    )


def maj_niveau_cible(sequence_id, connaissance_id, niveau_cible):
    """Fixe le niveau cible d'un lien (None pour effacer)."""
    execute(
        "UPDATE sequence_connaissance SET NiveauCible = ?, UpdatedAt = ? "
        "WHERE sequence_id = ? AND connaissance_id = ?",
        (niveau_cible, datetime.now(timezone.utc), sequence_id, connaissance_id),
    )


def maj_statut(sequence_id, connaissance_id, statut):
    """Fixe le statut d'un lien (None pour effacer)."""
    execute(
        "UPDATE sequence_connaissance SET Statut = ?, UpdatedAt = ? "
        "WHERE sequence_id = ? AND connaissance_id = ?",
        (statut, datetime.now(timezone.utc), sequence_id, connaissance_id),
    )
