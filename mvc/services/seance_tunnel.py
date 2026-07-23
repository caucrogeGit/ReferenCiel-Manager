# pyright: strict
"""Logique pure du tunnel d'édition de séance (ADR-032, miroir de sequence_tunnel).

Bornage de l'étape, complétion dérivée des données (jamais persistée), navigation.
La séance porte sa fiche (attributs SEQ-02) et sélectionne, parmi la liaison du
scénario appairé, les compétences qu'elle observe et leurs critères.
"""
from __future__ import annotations

from typing import Any, cast

ETAPES: tuple[str, ...] = ("fiche", "savoirs", "competences", "deroule", "gestion")

LIBELLES: dict[str, str] = {
    "fiche": "Fiche",
    "savoirs": "Savoirs associés",
    "competences": "Compétences observées",
    "deroule": "Déroulé",
    "gestion": "Gestion",
}


def parse_id(raw: object) -> "int | None":
    """Entier depuis une valeur de requête, ou None — jamais d'exception."""
    try:
        return int(cast("int", raw))
    except (TypeError, ValueError):
        return None


def borner_etape(raw: str) -> str:
    """Étape demandée, bornée à la liste connue (défaut : fiche)."""
    return raw if raw in ETAPES else "fiche"


def steps(seance: dict[str, Any], nb_savoirs_ouvrants: int, nb_competences: int, nb_elements: int) -> list[dict[str, Any]]:
    """Barre d'étapes : la complétion est DÉRIVÉE des données, jamais persistée.

    - Fiche : titre rempli (obligatoire à la création).
    - Savoirs associés (ADR-037) : au moins un savoir OUVRANT (validé, statut
      ouvrant pour la nature de la séquence) — c'est lui qui publie la séquence.
    - Compétences observées : au moins une compétence retenue. L'étape reste
      accessible même sans liaison de référentiel (elle invite alors à en poser
      une côté scénario).
    - Déroulé : au moins un élément (consigne, vidéo, QCM, TP, dépôt…).
    """
    return [
        {
            "key": "fiche",
            "label": LIBELLES["fiche"],
            "badge": "",
            "done": bool(seance.get("Titre")),
        },
        {
            "key": "savoirs",
            "label": LIBELLES["savoirs"],
            "badge": str(nb_savoirs_ouvrants) if nb_savoirs_ouvrants else "",
            "done": nb_savoirs_ouvrants > 0,
        },
        {
            "key": "competences",
            "label": LIBELLES["competences"],
            "badge": str(nb_competences) if nb_competences else "",
            "done": nb_competences > 0,
        },
        {
            "key": "deroule",
            "label": LIBELLES["deroule"],
            "badge": str(nb_elements) if nb_elements else "",
            "done": nb_elements > 0,
        },
        {
            # Gestion (ADR-038) : suppression (et futurs exports). Étape
            # d'outillage, hors complétude (drapeau `outil` : ni coche ni cercle).
            "key": "gestion",
            "label": LIBELLES["gestion"],
            "badge": "",
            "done": True,
            "outil": True,
        },
    ]


def navigation(etape: str) -> dict[str, Any]:
    """Position dans le tunnel et étapes précédente/suivante (None aux bornes)."""
    position = ETAPES.index(etape) + 1
    return {
        "etape": etape,
        "position": position,
        "total": len(ETAPES),
        "prev": (
            {"key": ETAPES[position - 2], "label": LIBELLES[ETAPES[position - 2]]}
            if position > 1
            else None
        ),
        "next": (
            {"key": ETAPES[position], "label": LIBELLES[ETAPES[position]]}
            if position < len(ETAPES)
            else None
        ),
    }
