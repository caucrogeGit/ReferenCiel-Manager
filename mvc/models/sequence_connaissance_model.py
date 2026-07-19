"""Lien Séquence ↔ Connaissance (ADR-028).

Une séquence retient des connaissances du référentiel de son scénario appairé,
et leur attribue un niveau cible (distinct du niveau officiel) et un statut dans
la progression. Écriture ciblée d'un seul lien par requête, comme les pivots du
tunnel scénario (évite les races entre requêtes HTMX concurrentes).
"""

from datetime import datetime, timezone

from core.database.db import fetch_all, fetch_one, execute, insert

# Statuts autorisés (ADR-028). L'ordre reflète la progression pédagogique.
STATUTS = ("prerequis", "apportee", "mobilisee", "consolidee")
STATUT_LABELS = {
    "prerequis": "Prérequis",
    "apportee": "Apportée",
    "mobilisee": "Mobilisée",
    "consolidee": "Consolidée",
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
