# pyright: strict
"""Espace professeur — « Mes classes » (lecture seule).

Vues de synthèse sur le socle scolaire pour le professeur **connecté**, filtrées
par son compte (`professeur.UserId = ?`) : sécurité au niveau **ligne** (row-level),
le professeur ne voit que les classes où il est affecté et les élèves qui y sont
inscrits. SQL visible et paramétré (esprit Forge). Aucune écriture : premier
incrément de l'espace professeur en consultation (tranche verticale Bloc A, ticket 07).
"""
from __future__ import annotations

from typing import Any

from core.database.db import fetch_all, fetch_one


def get_professeur_by_user(user_id: int) -> dict[str, Any] | None:
    """Le professeur rattaché à ce compte, ou None si le compte n'est lié à aucun."""
    return fetch_one(
        "SELECT Id AS id, Nom AS nom, Prenom AS prenom FROM professeur WHERE UserId = ?",
        (user_id,),
    )


def mes_affectations(professeur_id: int) -> list[dict[str, Any]]:
    """Une ligne par affectation du professeur : sa classe, l'année, le rôle et le
    nombre d'élèves inscrits dans cette classe pour cette année.

    L'affectation (`affectation_professeur_classe`) est le lien professeur ↔ classe
    ↔ année ; on compte les inscriptions de la même classe et de la même année.
    """
    return fetch_all(
        "SELECT apc.Id AS affectation_id, apc.Role AS role, "
        "apc.classe_id AS classe_id, apc.annee_scolaire_id AS annee_scolaire_id, "
        "c.Code AS classe_code, c.Libelle AS classe_libelle, "
        "nc.Code AS niveau_code, nc.Intitule AS niveau_intitule, "
        "asc2.Libelle AS annee_libelle, "
        "COUNT(DISTINCT ie.eleve_id) AS nb_eleves "
        "FROM affectation_professeur_classe apc "
        "JOIN classe c ON c.Id = apc.classe_id "
        "JOIN niveau_classe nc ON nc.Id = c.niveau_classe_id "
        "JOIN annee_scolaire asc2 ON asc2.Id = apc.annee_scolaire_id "
        "LEFT JOIN inscription_eleve ie "
        "  ON ie.classe_id = apc.classe_id AND ie.annee_scolaire_id = apc.annee_scolaire_id "
        "WHERE apc.professeur_id = ? "
        "GROUP BY apc.Id, apc.Role, apc.classe_id, apc.annee_scolaire_id, "
        "c.Code, c.Libelle, nc.Code, nc.Intitule, asc2.Libelle "
        "ORDER BY asc2.Libelle DESC, nc.Code, c.Code",
        (professeur_id,),
    )


def eleves_de_classe(classe_id: int, annee_scolaire_id: int) -> list[dict[str, Any]]:
    """Les élèves inscrits dans une classe pour une année donnée (nom, prénom, identifiant)."""
    return fetch_all(
        "SELECT e.Id AS id, e.Nom AS nom, e.Prenom AS prenom, e.Identifiant AS identifiant "
        "FROM inscription_eleve ie "
        "JOIN eleve e ON e.Id = ie.eleve_id "
        "WHERE ie.classe_id = ? AND ie.annee_scolaire_id = ? "
        "ORDER BY e.Nom, e.Prenom",
        (classe_id, annee_scolaire_id),
    )


def mes_classes(user_id: int) -> dict[str, Any] | None:
    """Vue complète « Mes classes » du compte : professeur + affectations + élèves.

    Renvoie None si le compte n'est rattaché à aucun professeur (compte non lié).
    """
    professeur = get_professeur_by_user(user_id)
    if professeur is None:
        return None
    affectations = mes_affectations(int(professeur["id"]))
    for affectation in affectations:
        affectation["eleves"] = eleves_de_classe(
            int(affectation["classe_id"]), int(affectation["annee_scolaire_id"])
        )
    return {"professeur": professeur, "affectations": affectations}
