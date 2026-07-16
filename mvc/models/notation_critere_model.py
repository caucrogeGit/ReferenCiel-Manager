# pyright: strict
"""Évaluation professeur — notation d'une activité par critères observables.

Le professeur note l'activité d'une séance au moyen des **critères observables**
(groupés par compétence, issus du référentiel), sur une échelle à **4 niveaux**.
Une `evaluation_activite` (find-or-create) porte l'évaluation du couple
(progression_seance, activité) ; chaque `evaluation_critere` fige le niveau d'un
critère (upsert sur la clé unique). SQL visible et paramétré.

Le `professeur_id` retenu est celui de l'**affectation** de la séquence (professeur
responsable) : le compte connecté n'est pas encore relié à une fiche `professeur`
(raffinement futur, cf. `professeur.UserId`, à l'image de `eleve.UserId`).
"""
from __future__ import annotations

from typing import Any

from core.database.db import execute, fetch_all, fetch_one, insert
from core.database.transaction import transaction

# Échelle à 4 niveaux (stockée dans evaluation_critere.Niveau).
NIVEAUX = ("non_atteint", "partiellement_atteint", "atteint", "depasse")


def _contexte(progression_seance_id: int) -> dict[str, Any] | None:
    """Résout la séance : activité à noter, élève, et professeur de l'affectation."""
    return fetch_one(
        "SELECT pp.Id AS pp_id, pp.progression_sequence_id AS progression_id, "
        "pa.Titre AS seance_titre, e.Nom AS nom, e.Prenom AS prenom, "
        "(SELECT MIN(Id) FROM activite a WHERE a.seance_id = pa.Id) AS activite_id "
        "FROM progression_seance pp "
        "JOIN seance pa ON pa.Id = pp.seance_id "
        "JOIN progression_sequence pe ON pe.Id = pp.progression_sequence_id "
        "JOIN eleve e ON e.Id = pe.eleve_id "
        "WHERE pp.Id = ?",
        (progression_seance_id,),
    )


def professeur_de_user(user_id: int) -> int | None:
    """La fiche professeur rattachée à ce compte, si le compte est lié."""
    row = fetch_one("SELECT Id AS id FROM professeur WHERE UserId = ?", (user_id,))
    return int(row["id"]) if row is not None else None


def _evaluation_existante(progression_seance_id: int, activite_id: int) -> int | None:
    row = fetch_one(
        "SELECT Id AS id FROM evaluation_activite "
        "WHERE progression_seance_id = ? AND activite_id = ? ORDER BY Id LIMIT 1",
        (progression_seance_id, activite_id),
    )
    return int(row["id"]) if row is not None else None


def get_grille(progression_seance_id: int) -> dict[str, Any] | None:
    """Grille de notation : compétences → critères (+ niveau déjà posé), si le
    seance a une activité à évaluer. None sinon."""
    ctx = _contexte(progression_seance_id)
    if ctx is None or ctx["activite_id"] is None:
        return None
    eval_id = _evaluation_existante(progression_seance_id, int(ctx["activite_id"])) or 0
    competences = fetch_all(
        "SELECT Id AS id, Code AS code, Intitule AS intitule FROM competence ORDER BY Code"
    )
    for comp in competences:
        comp["criteres"] = fetch_all(
            "SELECT c.Id AS id, c.Libelle AS libelle, ec.Niveau AS niveau "
            "FROM critere_observable c "
            "LEFT JOIN evaluation_critere ec "
            "  ON ec.critere_id = c.Id AND ec.evaluation_activite_id = ? "
            "WHERE c.competence_id = ? ORDER BY c.Id",
            (eval_id, comp["id"]),
        )
    return {
        "progression_seance_id": progression_seance_id,
        "progression_id": ctx["progression_id"],
        "seance_titre": ctx["seance_titre"],
        "eleve": f"{ctx['prenom']} {ctx['nom']}",
        "niveaux": list(NIVEAUX),
        "competences": competences,
    }


def enregistrer_notation(
    progression_seance_id: int, niveaux: dict[int, str], user_id: int | None = None
) -> dict[str, Any] | None:
    """Enregistre les niveaux des critères notés (find-or-create de l'évaluation).

    `niveaux` : {critere_id: niveau}. Les niveaux hors échelle ou vides sont
    ignorés. Le professeur attribué est celui du compte connecté (`user_id` lié à
    une fiche `professeur`) ; à défaut, celui de l'affectation. Renvoie {notes} ou
    None si la séance n'a pas d'activité à évaluer.
    """
    ctx = _contexte(progression_seance_id)
    if ctx is None or ctx["activite_id"] is None:
        return None
    activite_id = int(ctx["activite_id"])
    # ADR-022 : le professeur attribué est celui du compte connecté (l'affectation,
    # qui portait un professeur, a été supprimée). Sans prof identifiable, on n'attribue pas.
    professeur_id = professeur_de_user(user_id) if user_id is not None else None
    if professeur_id is None:
        return None
    valides = {cid: niv for cid, niv in niveaux.items() if niv in NIVEAUX}

    with transaction() as tx:
        eval_id = _evaluation_existante(progression_seance_id, activite_id)
        if eval_id is None:
            eval_id = insert(
                "INSERT INTO evaluation_activite "
                "(DateEvaluation, progression_seance_id, activite_id, professeur_id, CreatedAt, UpdatedAt) "
                "VALUES (NOW(), ?, ?, ?, NOW(), NOW())",
                (progression_seance_id, activite_id, professeur_id),
                tx=tx,
            )
        for critere_id, niveau in valides.items():
            execute(
                "INSERT INTO evaluation_critere "
                "(Niveau, evaluation_activite_id, critere_id, CreatedAt, UpdatedAt) "
                "VALUES (?, ?, ?, NOW(), NOW()) "
                "ON DUPLICATE KEY UPDATE Niveau = VALUES(Niveau), UpdatedAt = NOW()",
                (niveau, eval_id, critere_id),
                tx=tx,
            )
    return {"notes": len(valides)}
