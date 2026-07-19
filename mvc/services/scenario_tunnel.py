# pyright: strict
"""Logique pure du tunnel d'édition de scénario (ADR-019, ADR-021).

Extraite de `ScenarioEditeurController` pour rester testable sans HTTP :
bornage de l'étape, complétion dérivée des données (jamais persistée),
analyse des identifiants soumis, navigation entre étapes et ouverture du
maître-détail sur la sélection existante.
"""
from __future__ import annotations

from typing import Any, cast

# État du tunnel (ADR-021) : les 4 étapes et leurs libellés. La complétion
# n'est jamais persistée, elle est dérivée des données (voir `steps`).
ETAPES: tuple[str, ...] = ("titre", "contexte", "liaison", "ressources")

LIBELLES: dict[str, str] = {
    "titre": "Titre",
    "contexte": "Contexte",
    "liaison": "Liaison référentiel",
    "ressources": "Ressources",
}

# Les 5 champs cpro du contexte, tous obligatoires (d'où le all() de `steps`).
_CHAMPS_CONTEXTE: tuple[str, ...] = (
    "DescriptionContexte",
    "Problematique",
    "MaterielsLogiciels",
    "LiensAssocies",
    "EspacesFormation",
)


def parse_id(raw: object) -> "int | None":
    """Entier depuis une valeur de requête, ou None — jamais d'exception."""
    try:
        return int(cast("int", raw))
    except (TypeError, ValueError):
        return None


def parse_ids(raw: Any) -> list[int]:
    """Identifiants strictement positifs, dédoublonnés, dans l'ordre soumis.

    `raw` vient d'un champ multiple du corps de requête : liste, valeur seule
    ou absence. Les valeurs non numériques sont ignorées silencieusement.
    """
    if isinstance(raw, list):
        values: list[Any] = cast("list[Any]", raw)
    elif raw:
        values = [raw]
    else:
        values = []
    out: list[int] = []
    for value in values:
        try:
            n = int(value)
        except (TypeError, ValueError):
            continue
        if n > 0 and n not in out:
            out.append(n)
    return out


def borner_etape(raw: str) -> str:
    """Étape demandée, bornée à la liste connue (défaut : titre)."""
    return raw if raw in ETAPES else "titre"


def steps(
    scenario: dict[str, Any],
    activite_ids: list[int],
    critere_ids: list[int],
) -> list[dict[str, Any]]:
    """Barre d'étapes : la complétion est DÉRIVÉE des données.

    Rien n'est persisté pour l'UI ; l'indicateur de chaque étape est aligné sur
    la règle de statut (recalculer_statut) : « finalisé » = contexte complet ET
    au moins une activité ET au moins un critère.
    """
    #  - Titre : rempli dès la création (obligatoire).
    #  - Contexte : les 5 champs cpro sont tous obligatoires (d'où all()).
    #  - Liaison : au moins une activité ET un critère (contribue à « finalisé »).
    #  - Ressources : facultatives -> l'étape ne bloque jamais.
    contexte_complet = all(scenario.get(champ) for champ in _CHAMPS_CONTEXTE)
    liaison_complete = len(activite_ids) > 0 and len(critere_ids) > 0

    return [
        {
            "key": "titre",
            "label": LIBELLES["titre"],
            "badge": "",
            "done": bool(scenario.get("Titre")),
        },
        {
            "key": "contexte",
            "label": LIBELLES["contexte"],
            "badge": "",
            "done": contexte_complet,
        },
        {
            "key": "liaison",
            # Le code du référentiel (ex. « ciel-2tne ») est rappelé sous le titre.
            "label": LIBELLES["liaison"],
            "badge": "",
            "done": liaison_complete,
        },
        {
            "key": "ressources",
            "label": LIBELLES["ressources"],
            "badge": "",
            "done": True,
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


def selection_courante(
    arbre: "dict[str, Any] | None", pole_raw: object, competence_raw: object
) -> "tuple[int | None, int | None]":
    """Pôle et compétence actifs, ou None si aucun n'est encore choisi.

    À l'arrivée sur l'étape (aucun `pole`/`competence` dans la requête), on ne
    présélectionne rien : chaque colonne de détail invite explicitement à
    choisir un item. L'item actif est porté par l'URL (lien maître, hx-get) ou
    par le formulaire de cochage (hx-post) — jamais deviné par défaut.
    """
    if not arbre:
        return None, None
    return parse_id(pole_raw), parse_id(competence_raw)


def ouvrir_sur_selection(
    arbre: "dict[str, Any] | None",
    pole_id: "int | None",
    competence_id: "int | None",
    activite_ids: list[int],
    critere_ids: list[int],
) -> "tuple[int | None, int | None]":
    """À l'arrivée sur l'étape (aucun item explicitement demandé), ouvre le
    premier pôle et la première compétence QUI ONT des cases cochées, pour
    montrer d'emblée les sélections du scénario (sinon l'utilisateur voit un
    badge de comptage sans pouvoir le rapprocher d'un détail). Un scénario
    vierge reste sans rien d'ouvert. N'écrase jamais un choix explicite."""
    if not arbre:
        return pole_id, competence_id
    if pole_id is None:
        pole_id = next(
            (int(p["Id"]) for p in arbre.get("poles", [])
             if any(int(a["Id"]) in activite_ids for a in p.get("activites", []))),
            None,
        )
    if competence_id is None:
        competence_id = next(
            (int(c["Id"]) for c in arbre.get("competences", [])
             if any(int(cr["Id"]) in critere_ids for cr in c.get("criteres", []))),
            None,
        )
    return pole_id, competence_id


def slug(texte: str) -> str:
    """Nom de fichier sûr : alphanumériques conservés, le reste en tirets."""
    brut = "".join(ch if ch.isalnum() else "-" for ch in texte.lower())
    propre = "-".join(part for part in brut.split("-") if part)
    return propre[:60] or "scenario"
