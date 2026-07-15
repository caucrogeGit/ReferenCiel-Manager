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


def mes_classes_liste(professeur_id: int) -> list[dict[str, Any]]:
    """Une ligne par classe du professeur : sa classe, le niveau, l'année et le
    nombre d'élèves rattachés.

    ADR-022 : le lien professeur ↔ classe est le pivot `classe_professeur`
    (l'année se déduit de la classe) ; les élèves sont rattachés directement à la
    classe (`eleve.classe_id`, plus d'`inscription_eleve`).
    """
    return fetch_all(
        "SELECT c.Id AS classe_id, "
        "c.Code AS classe_code, c.Libelle AS classe_libelle, "
        "nc.Code AS niveau_code, nc.Intitule AS niveau_intitule, "
        "asc2.Libelle AS annee_libelle, "
        "COUNT(DISTINCT e.Id) AS nb_eleves "
        "FROM classe_professeur cp "
        "JOIN classe c ON c.Id = cp.classe_id "
        "JOIN niveau_classe nc ON nc.Id = c.niveau_classe_id "
        "JOIN annee_scolaire asc2 ON asc2.Id = c.annee_scolaire_id "
        "LEFT JOIN eleve e ON e.classe_id = c.Id "
        "WHERE cp.professeur_id = ? "
        "GROUP BY c.Id, c.Code, c.Libelle, nc.Code, nc.Intitule, asc2.Libelle "
        "ORDER BY asc2.Libelle DESC, nc.Code, c.Code",
        (professeur_id,),
    )


def eleves_de_classe(classe_id: int) -> list[dict[str, Any]]:
    """Les élèves rattachés à une classe (nom, prénom, identifiant)."""
    return fetch_all(
        "SELECT e.Id AS id, e.Nom AS nom, e.Prenom AS prenom, e.Identifiant AS identifiant "
        "FROM eleve e "
        "WHERE e.classe_id = ? "
        "ORDER BY e.Nom, e.Prenom",
        (classe_id,),
    )


def mes_classes(user_id: int) -> dict[str, Any] | None:
    """Vue complète « Mes classes » du compte : professeur + classes + élèves.

    Renvoie None si le compte n'est rattaché à aucun professeur (compte non lié).
    """
    professeur = get_professeur_by_user(user_id)
    if professeur is None:
        return None
    classes = mes_classes_liste(int(professeur["id"]))
    for classe in classes:
        classe["eleves"] = eleves_de_classe(int(classe["classe_id"]))
    return {"professeur": professeur, "classes": classes}
