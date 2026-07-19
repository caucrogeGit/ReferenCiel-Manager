# pyright: strict
"""Logique pure du tunnel d'édition de séquence (miroir de scenario_tunnel).

Même patron que le tunnel scénario (ADR-019, ADR-021) : bornage de l'étape,
complétion dérivée des données (jamais persistée), navigation entre étapes.
La séquence porte le cadre institutionnel (SEQ-02) et les connaissances
associées (ADR-028) ; sa liaison au référentiel passe par le scénario appairé.
"""
from __future__ import annotations

from typing import Any, cast

ETAPES: tuple[str, ...] = ("titre", "cadre", "connaissances", "seances")

LIBELLES: dict[str, str] = {
    "titre": "Titre",
    "cadre": "Cadre institutionnel",
    "connaissances": "Savoirs associés",
    "seances": "Séances",
}


def parse_id(raw: object) -> "int | None":
    """Entier depuis une valeur de requête, ou None — jamais d'exception."""
    try:
        return int(cast("int", raw))
    except (TypeError, ValueError):
        return None


def borner_etape(raw: str) -> str:
    """Étape demandée, bornée à la liste connue (défaut : titre)."""
    return raw if raw in ETAPES else "titre"


def steps(
    sequence: dict[str, Any],
    nb_connaissances: int,
    nb_seances: int,
) -> list[dict[str, Any]]:
    """Barre d'étapes : la complétion est DÉRIVÉE des données, jamais persistée.

    - Titre : le titre est rempli (obligatoire à la création).
    - Cadre institutionnel : facultatif (ne bloque jamais).
    - Savoirs associés : au moins une connaissance retenue. L'étape reste
      accessible même sans référentiel : on peut y en rattacher un (via le
      scénario appairé) pour débloquer la sélection.
    - Séances : au moins une séance rattachée.
    """
    return [
        {
            "key": "titre",
            "label": LIBELLES["titre"],
            "badge": "",
            "done": bool(sequence.get("Titre")),
        },
        {
            "key": "cadre",
            "label": LIBELLES["cadre"],
            "badge": "",
            "done": True,
        },
        {
            "key": "connaissances",
            "label": LIBELLES["connaissances"],
            "badge": str(nb_connaissances) if nb_connaissances else "",
            "done": nb_connaissances > 0,
        },
        {
            "key": "seances",
            "label": LIBELLES["seances"],
            "badge": str(nb_seances) if nb_seances else "",
            "done": nb_seances > 0,
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
