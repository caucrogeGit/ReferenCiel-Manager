# pyright: strict
"""Construction du PDF d'un scénario finalisé (ADR-024).

Contenu MÉTIER, spécifique à l'application : rassemble les données du scénario
(titre, contexte, liaison au référentiel, ressources), rend le template
`app/scenario_editeur/pdf.html`, puis délègue la conversion HTML->PDF à
`services.pdf.render_pdf` (générique, destinée à un futur opt-in).
"""
from typing import Any

from core.templating.manager import template_manager

from mvc.models.referentiel_atelier_model import get_arbre, get_referentiel
from mvc.models.scenario_editeur_model import (
    get_activite_ids,
    get_co_auteur_ids,
    get_critere_ids,
    get_scenario,
    list_professeurs,
    list_ressources,
)
from mvc.services.pdf import render_pdf

# Champs de contexte affichés, avec leur libellé (miroir de _etape_contexte.html).
_CONTEXTE: tuple[tuple[str, str], ...] = (
    ("DescriptionContexte", "Description du contexte / mise en situation professionnelle"),
    ("Problematique", "Problématique liée au métier / missions à réaliser"),
    ("MaterielsLogiciels", "Matériels et/ou logiciels utilisés"),
    ("LiensAssocies", "Liens associés à ce scénario"),
    ("EspacesFormation", "Espace(s) de formation"),
)


def _contexte(scenario: dict[str, Any]) -> list[dict[str, str]]:
    """Champs de contexte renseignés, dans l'ordre du formulaire."""
    return [
        {"libelle": libelle, "valeur": str(scenario[col])}
        for col, libelle in _CONTEXTE
        if scenario.get(col)
    ]


def _activites(arbre: dict[str, Any], activite_ids: list[int]) -> list[dict[str, Any]]:
    """Activités cochées, avec le pôle d'appartenance."""
    retenues: list[dict[str, Any]] = []
    for pole in arbre.get("poles", []):
        for act in pole.get("activites", []):
            if act["Id"] in activite_ids:
                retenues.append(
                    {"code": act["Code"], "intitule": act["Intitule"], "pole": pole["Intitule"]}
                )
    return retenues


def _competences(arbre: dict[str, Any], critere_ids: list[int]) -> list[dict[str, Any]]:
    """Compétences ayant au moins un critère coché, avec leurs critères retenus
    (libellé, savoir-être, indicateurs de réussite)."""
    retenues: list[dict[str, Any]] = []
    for comp in arbre.get("competences", []):
        criteres = [
            {
                "libelle": c["Libelle"],
                "savoir_etre": bool(c.get("SavoirEtre")),
                "indicateurs": [ind["Libelle"] for ind in c.get("indicateurs", [])],
            }
            for c in comp.get("criteres", [])
            if c["Id"] in critere_ids
        ]
        if criteres:
            retenues.append(
                {
                    "code": comp["Code"],
                    "intitule": comp["Intitule"],
                    "cc_codes": comp.get("cc_codes", []),
                    "criteres": criteres,
                }
            )
    return retenues


def _co_auteurs(scenario_id: int) -> list[str]:
    """Noms des professeurs co-auteurs (co-intervention)."""
    ids = set(get_co_auteur_ids(scenario_id))
    if not ids:
        return []
    return [
        f"{p['Prenom']} {p['Nom']}"
        for p in list_professeurs()
        if p["Id"] in ids
    ]


def construire_pdf(scenario_id: int) -> bytes:
    """Assemble le PDF d'un scénario. L'appelant garantit qu'il est finalisé."""
    scenario = get_scenario(scenario_id)
    if scenario is None:
        raise ValueError(f"scénario {scenario_id} introuvable")

    referentiel_id = scenario.get("referentiel_id")
    referentiel = get_referentiel(int(referentiel_id)) if referentiel_id else None
    arbre: dict[str, Any] = (
        get_arbre(int(referentiel_id)) if referentiel_id else {"poles": [], "competences": []}
    )

    context: dict[str, Any] = {
        "scenario": scenario,
        "referentiel": referentiel,
        "co_auteurs": _co_auteurs(scenario_id) if scenario.get("CoIntervention") else [],
        "contexte": _contexte(scenario),
        "activites": _activites(arbre, get_activite_ids(scenario_id)),
        "competences": _competences(arbre, get_critere_ids(scenario_id)),
        "ressources": list_ressources(scenario_id),
    }
    html = template_manager.render("app/scenario_editeur/pdf.html", context)
    return render_pdf(html)
