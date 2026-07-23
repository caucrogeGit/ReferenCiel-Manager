# pyright: strict
"""Regroupement de lignes consécutives pour les listes de cartes (ADR-002 UI).

Les pages de cartes (scénarios, séquences, séances) classent leurs cartes par
sections : référentiel pour les deux premières, séquence pour la troisième.
L'ORDRE VIENT DU SQL (les lignes arrivent déjà triées par clé de groupe) ; ici
on ne fait que découper la liste en sections consécutives, sans re-trier.
"""
from __future__ import annotations

from typing import Any, Callable


def grouper(
    rows: list[dict[str, Any]],
    libelle: "Callable[[dict[str, Any]], str | None]",
    defaut: str,
) -> list[dict[str, Any]]:
    """Découpe `rows` en groupes consécutifs [{label, cartes}], ordre préservé.

    La clé « cartes » (et non « items ») évite la collision Jinja avec dict.items.

    `libelle` extrait l'étiquette de groupe d'une ligne ; vide ou None retombe
    sur `defaut` (ex. « Hors référentiel »).
    """
    groupes: list[dict[str, Any]] = []
    for row in rows:
        label = libelle(row) or defaut
        if not groupes or groupes[-1]["label"] != label:
            groupes.append({"label": label, "cartes": []})
        groupes[-1]["cartes"].append(row)
    return groupes


def libelle_referentiel(row: dict[str, Any]) -> "str | None":
    """Étiquette de section d'un référentiel : « Formation · identifiant ».

    Attend les colonnes `referentiel_identifiant` et `formation_intitule`
    (jointes par les requêtes de liste) ; None si la ligne est hors référentiel.
    """
    identifiant = row.get("referentiel_identifiant")
    if not identifiant:
        return None
    formation = row.get("formation_intitule")
    return f"{formation} · {identifiant}" if formation else str(identifiant)
