# pyright: strict
"""Niveaux de maîtrise d'un critère — grille officielle CIEL (ADR-032/033).

La **donnée métier est le NIVEAU**, pas la couleur (simple représentation
visuelle). « Non observé » est un état **distinct du rouge** : l'élève n'a pas été
placé en situation d'observation, il ne doit pas être pénalisé.

Les seuils du positionnement (« 0 / 1 / 2-3 / 4 observables » de l'exemple à
quatre observables) ne sont **pas figés** : `suggerer_niveau` calcule sur le
nombre **réel** d'indicateurs. Et ce n'est qu'une **suggestion** — le professeur
arbitre (règle d'évaluation, ADR-032).
"""
from __future__ import annotations

from typing import Any

# code, niveau (None = non observé), libellé officiel, couleur, explication élève.
NIVEAUX: list[dict[str, Any]] = [
    {"code": "NON_OBSERVE", "niveau": None, "libelle": "Non observé", "couleur": "gris",
     "explication": "L'élève n'a pas encore été placé en situation d'observation."},
    {"code": "NIVEAU_1", "niveau": 1, "libelle": "Non réalisé", "couleur": "rouge",
     "explication": "Le résultat attendu n'est pas obtenu."},
    {"code": "NIVEAU_2", "niveau": 2, "libelle": "Réalisation partielle", "couleur": "orange",
     "explication": "Une partie est correcte, mais le travail doit être repris."},
    {"code": "NIVEAU_3", "niveau": 3, "libelle": "Réalisation satisfaisante", "couleur": "vert_clair",
     "explication": "Le travail répond aux attentes principales."},
    {"code": "NIVEAU_4", "niveau": 4, "libelle": "Réalisation très satisfaisante", "couleur": "vert_fonce",
     "explication": "Le travail répond complètement aux attentes et est maîtrisé."},
]

CODES: tuple[str, ...] = tuple(str(n["code"]) for n in NIVEAUX)

# Le code positionnable (hors « non observé »), pour les boutons de la feuille.
NIVEAUX_POSITIONNABLES: list[dict[str, Any]] = [n for n in NIVEAUX if n["niveau"] is not None]

_PAR_CODE: dict[str, dict[str, Any]] = {str(n["code"]): n for n in NIVEAUX}


def niveau(code: "str | None") -> dict[str, Any]:
    """Descripteur d'un niveau par son code (None ou inconnu → non observé)."""
    return _PAR_CODE.get(code or "NON_OBSERVE", _PAR_CODE["NON_OBSERVE"])


def suggerer_niveau(nb_valides: int, nb_total: int) -> str:
    """Niveau SUGGÉRÉ à partir du nombre d'indicateurs validés sur le total réel.

    Reproduit l'exemple à 4 observables (0→1, 1→2, 2-3→3, 4→4) sans figer ces
    nombres : 0 → Non réalisé ; tous → Très satisfaisant ; < 50 % → Partielle ;
    ≥ 50 % → Satisfaisante. Le professeur reste seul juge (ADR-032).
    """
    if nb_total <= 0:
        return "NON_OBSERVE"
    if nb_valides <= 0:
        return "NIVEAU_1"
    if nb_valides >= nb_total:
        return "NIVEAU_4"
    return "NIVEAU_2" if (nb_valides / nb_total) < 0.5 else "NIVEAU_3"
