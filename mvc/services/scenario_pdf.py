# pyright: strict
"""Construction du PDF d'un scénario finalisé (ADR-024).

Contenu MÉTIER, spécifique à l'application : rassemble les données du scénario
(titre, contexte, liaison au référentiel, ressources), rend le template
`app/scenario_editeur/pdf.html`, puis délègue la conversion HTML->PDF à
`services.pdf.render_pdf` (générique, destinée à un futur opt-in).
"""
from typing import Any

from core.templating.manager import template_manager

from mvc.models.referentiel_atelier_model import (
    get_arbre,
    get_referentiel,
    liens_activite_competence,
)
from mvc.models.scenario_editeur_model import (
    get_activite_ids,
    get_co_auteur_ids,
    get_critere_ids,
    get_scenario,
    list_professeurs,
    list_ressources,
)
from mvc.models.sequence_connaissance_model import (
    get_connaissances_retenues,
    get_sequence_id_for_scenario,
)
from mvc.models.savoir_libre_model import get_savoirs_libres
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


def _competences_par_id(arbre: dict[str, Any], critere_ids: list[int]) -> dict[int, dict[str, Any]]:
    """comp_id -> compétence (code, intitulé, CCx, critères cochés) pour les seules
    compétences ayant au moins un critère coché. L'ordre suit l'arbre (C01, C03…)."""
    out: dict[int, dict[str, Any]] = {}
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
            out[comp["Id"]] = {
                "code": comp["Code"],
                "intitule": comp["Intitule"],
                "cc_codes": comp.get("cc_codes", []),
                "criteres": criteres,
            }
    return out


def _activites(
    arbre: dict[str, Any],
    activite_ids: list[int],
    comp_par_id: dict[int, dict[str, Any]],
    liens: dict[int, set[int]],
) -> list[dict[str, Any]]:
    """Activités cochées AVEC leurs compétences évaluées (critères cochés).

    Une activité dont aucune compétence liée n'a de critère coché est OMISE.
    Une compétence mobilisée par plusieurs activités apparaît sous chacune.
    """
    retenues: list[dict[str, Any]] = []
    for pole in arbre.get("poles", []):
        for act in pole.get("activites", []):
            if act["Id"] not in activite_ids:
                continue
            lies = liens.get(act["Id"], set())
            # Ordre des compétences = ordre de comp_par_id (arbre : C01, C03…).
            competences = [comp for cid, comp in comp_par_id.items() if cid in lies]
            if not competences:
                continue
            retenues.append(
                {
                    "code": act["Code"],
                    "intitule": act["Intitule"],
                    "pole": pole["Intitule"],
                    "competences": competences,
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


def assembler_scenario(scenario_id: int) -> dict[str, Any]:
    """Rassemble les données d'un scénario pour l'export (PDF, Markdown, JSON).

    Structure commune : `scenario`, `referentiel`, `co_auteurs`, `contexte`
    (libellé/valeur), `activites` (avec compétences et critères) et `ressources`.
    """
    scenario = get_scenario(scenario_id)
    if scenario is None:
        raise ValueError(f"scénario {scenario_id} introuvable")

    referentiel_id = scenario.get("referentiel_id")
    referentiel = get_referentiel(int(referentiel_id)) if referentiel_id else None
    arbre: dict[str, Any] = (
        get_arbre(int(referentiel_id)) if referentiel_id else {"poles": [], "competences": []}
    )

    comp_par_id = _competences_par_id(arbre, get_critere_ids(scenario_id))
    liens = liens_activite_competence(int(referentiel_id)) if referentiel_id else {}

    # Savoirs de la séquence appairée : connaissances structurées si référentiel
    # (ADR-028), sinon savoirs libres saisis par le professeur (ADR-030).
    sequence_id = get_sequence_id_for_scenario(scenario_id)
    connaissances: list[dict[str, Any]] = (
        get_connaissances_retenues(sequence_id, int(referentiel_id))
        if sequence_id is not None and referentiel_id else []
    )
    savoirs_libres: list[str] = (
        [str(s["Libelle"]) for s in get_savoirs_libres(sequence_id)]
        if sequence_id is not None and not referentiel_id else []
    )
    return {
        "scenario": scenario,
        "referentiel": referentiel,
        "co_auteurs": _co_auteurs(scenario_id) if scenario.get("CoIntervention") else [],
        "contexte": _contexte(scenario),
        "activites": _activites(arbre, get_activite_ids(scenario_id), comp_par_id, liens),
        "connaissances": connaissances,
        "savoirs_libres": savoirs_libres,
        "ressources": list_ressources(scenario_id),
    }


def construire_pdf(scenario_id: int) -> bytes:
    """Assemble le PDF d'un scénario. L'appelant garantit qu'il est finalisé."""
    html = template_manager.render(
        "app/scenario_editeur/pdf.html", assembler_scenario(scenario_id)
    )
    return render_pdf(html)
