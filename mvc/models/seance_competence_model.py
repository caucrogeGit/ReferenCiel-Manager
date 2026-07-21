"""Compétences et critères observés par une séance (ADR-032, phase A2).

Cascade sans double saisie : la séance sélectionne PARMI la liaison du scénario
appairé (via la séquence 1-1). Elle ne voit que les critères déjà liés par le
scénario, groupés par compétence.
"""

from datetime import datetime, timezone

from core.database.db import fetch_all, fetch_one, execute, insert
from mvc.models.referentiel_atelier_model import get_arbre
from mvc.models.scenario_editeur_model import get_scenario, get_critere_ids

# Rôle d'une compétence dans la séance. « Évaluée » implique observée/assessée.
ROLES = ("travaillee", "evaluee")
ROLE_LABELS = {"travaillee": "Travaillée", "evaluee": "Évaluée"}


def get_scenario_id_for_seance(seance_id):
    """Scénario appairé à la séance (via la séquence). None si aucun."""
    row = fetch_one(
        "SELECT ss.scenario_id FROM seance se "
        "JOIN scenario_sequence ss ON ss.sequence_id = se.sequence_id "
        "WHERE se.Id = ? LIMIT 1",
        (seance_id,),
    )
    return row["scenario_id"] if row else None


def get_arbre_liaison(scenario_id):
    """Compétences → critères que le scénario a liés (avec leurs indicateurs).

    C'est le périmètre dans lequel la séance choisit ce qu'elle observe.
    """
    scenario = get_scenario(scenario_id)
    ref_id = scenario.get("referentiel_id") if scenario else None
    if not ref_id:
        return []
    arbre = get_arbre(int(ref_id))
    critere_ids = set(get_critere_ids(scenario_id))
    groupes = []
    for comp in arbre.get("competences", []):
        criteres = [c for c in comp.get("criteres", []) if c["Id"] in critere_ids]
        if criteres:
            groupes.append({
                "Id": comp["Id"], "Code": comp["Code"], "Intitule": comp["Intitule"],
                "criteres": criteres,
            })
    return groupes


def get_competences_observees(seance_id):
    """Compétences observées par la séance, indexées par competence_id → rôle."""
    rows = fetch_all(
        "SELECT competence_id, Role FROM seance_competence WHERE seance_id = ?", (seance_id,)
    )
    return {r["competence_id"]: r["Role"] for r in rows}


def get_criteres_observes(seance_id):
    """Ensemble des critères observés par la séance."""
    rows = fetch_all(
        "SELECT critere_observable_id FROM seance_critere WHERE seance_id = ?", (seance_id,)
    )
    return {r["critere_observable_id"] for r in rows}


def basculer_competence(seance_id, competence_id, role):
    """Ajoute/retire une compétence observée (rôle par défaut : travaillée)."""
    existe = fetch_one(
        "SELECT Id FROM seance_competence WHERE seance_id = ? AND competence_id = ?",
        (seance_id, competence_id),
    )
    if existe:
        execute(
            "DELETE FROM seance_competence WHERE seance_id = ? AND competence_id = ?",
            (seance_id, competence_id),
        )
    else:
        now = datetime.now(timezone.utc)
        insert(
            "INSERT INTO seance_competence (seance_id, competence_id, Role, CreatedAt, UpdatedAt) "
            "VALUES (?, ?, ?, ?, ?)",
            (seance_id, competence_id, role if role in ROLES else "travaillee", now, now),
        )


def maj_role(seance_id, competence_id, role):
    """Change le rôle d'une compétence observée."""
    if role not in ROLES:
        return
    execute(
        "UPDATE seance_competence SET Role = ?, UpdatedAt = ? "
        "WHERE seance_id = ? AND competence_id = ?",
        (role, datetime.now(timezone.utc), seance_id, competence_id),
    )


def basculer_critere(seance_id, critere_id):
    """Ajoute/retire un critère observé."""
    existe = fetch_one(
        "SELECT Id FROM seance_critere WHERE seance_id = ? AND critere_observable_id = ?",
        (seance_id, critere_id),
    )
    if existe:
        execute(
            "DELETE FROM seance_critere WHERE seance_id = ? AND critere_observable_id = ?",
            (seance_id, critere_id),
        )
    else:
        now = datetime.now(timezone.utc)
        insert(
            "INSERT INTO seance_critere (seance_id, critere_observable_id, CreatedAt, UpdatedAt) "
            "VALUES (?, ?, ?, ?)",
            (seance_id, critere_id, now, now),
        )
