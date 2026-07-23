"""Édition des savoirs associés d'une SÉANCE (ADR-037, descend l'ADR-028).

Maître-détail compétence → connaissances, dans le tunnel de la séance.
Le SCÉNARIO reste la source canonique (ADR-036) : seules ses compétences
retenues (critères cochés) sont actives ; les statuts proposés suivent la
nature de la séquence (héritée). Chaque requête écrit un seul lien puis
renvoie le fragment #savoirs-seance (ou redirige vers l'éditeur sans JS).
"""

from core.http.request import Request
from core.http.response import Response
from core.mvc.controller import BaseController

from mvc.helpers.htmx import est_htmx
from mvc.models.seance_connaissance_model import (
    STATUT_LABELS,
    NIVEAUX_TAXONOMIE,
    get_arbre_connaissances,
    get_liens_by_seance,
    lier,
    delier,
    maj_niveau_cible,
    maj_statut,
    referentiel_et_scenario_de_seance,
    competences_retenues_au_scenario_de_seance,
    competence_de_connaissance,
)
from mvc.models.seance_model import get_seance_by_id
from mvc.models.sequence_model import recalculer_statut as recalculer_statut_sequence
from mvc.services.sequence_tunnel import (
    savoir_ouvrant,
    statuts_pour_nature,
)

_NIVEAUX = [("", "—"), ("1", "1"), ("2", "2"), ("3", "3"), ("4", "4")]


def _parse_id(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _query(request, name, default=""):
    values = request.params.get(name, [default])
    return values[0] if values else default


def contexte_savoirs(seance_id, competence_id=None):
    """Contexte du bloc savoirs de la séance : arbre, liens, compétence active."""
    ref_id, _scenario_id, nature = referentiel_et_scenario_de_seance(seance_id)
    if ref_id is None:
        # Séquence hors référentiel : les savoirs libres restent au niveau
        # séquence (ADR-030/ADR-037) — la séance n'a rien à saisir ici.
        return {
            "seance_id": seance_id,
            "ref_absent": True,
            "competences": [],
            "liens": {},
            "competence_id": None,
        }
    liens = get_liens_by_seance(seance_id)
    competences_actives = competences_retenues_au_scenario_de_seance(seance_id)
    # Le SCÉNARIO est la source canonique (ADR-036/037) : seules ses compétences
    # retenues sont présentées — plus celles portant des savoirs hérités d'un
    # périmètre antérieur (signalées « hors scénario », à nettoyer).
    competences = [
        comp for comp in get_arbre_connaissances(ref_id)
        if comp["Id"] in competences_actives
        or any(k["Id"] in liens for k in comp.get("connaissances", []))
    ]
    competences_ouvertes = {
        comp["Id"]
        for comp in competences
        for k in comp.get("connaissances", [])
        if (lien := liens.get(k["Id"])) and savoir_ouvrant(lien, nature)
    }
    statuts_nature = [("", "—")] + [(v, STATUT_LABELS[v]) for v in statuts_pour_nature(nature)]
    return {
        "seance_id": seance_id,
        "ref_absent": False,
        "competences": competences,
        "competences_actives": competences_actives,
        "competences_ouvertes": competences_ouvertes,
        "liens": liens,
        "competence_id": competence_id,
        "niveaux": _NIVEAUX,
        "niveaux_taxonomie": NIVEAUX_TAXONOMIE,
        "statuts": statuts_nature,
        "statuts_nature_codes": statuts_pour_nature(nature),
        "statut_labels": STATUT_LABELS,
    }


class SeanceConnaissanceController(BaseController):

    @staticmethod
    def _rendre(request: Request, seance_id: int, competence_id, message_garde=None) -> Response:
        if not est_htmx(request):
            return BaseController.redirect(
                f"/seance/editeur/{seance_id}?etape=savoirs", request=request
            )
        context = contexte_savoirs(seance_id, competence_id)
        if message_garde:
            context["message_garde"] = message_garde
        # Stepper recalculé hors-bande : la complétion de l'étape suit chaque
        # cochage (import local, évite le cycle contrôleur <-> contrôleur).
        from mvc.controllers.seance_editeur_controller import SeanceEditeurController
        context.update(SeanceEditeurController._contexte_stepper(seance_id, "savoirs"))
        return BaseController.render(
            "app/seance_editeur/_savoirs.html", context=context, request=request
        )

    @staticmethod
    def afficher(request: Request) -> Response:
        seance_id = _parse_id(request.route("id"))
        if seance_id is None or get_seance_by_id(seance_id) is None:
            return BaseController.not_found()
        competence_id = _parse_id(_query(request, "competence"))
        return SeanceConnaissanceController._rendre(request, seance_id, competence_id)

    @staticmethod
    def basculer(request: Request) -> Response:
        seance_id = _parse_id(request.route("id"))
        seance = get_seance_by_id(seance_id) if seance_id is not None else None
        if seance_id is None or seance is None:
            return BaseController.not_found()
        connaissance_id = _parse_id(request.form("connaissance", ""))
        competence_id = _parse_id(request.form("competence", ""))
        if connaissance_id is not None:
            liens = get_liens_by_seance(seance_id)
            if connaissance_id in liens:
                delier(seance_id, connaissance_id)
            else:
                # Le scénario est la source canonique (ADR-036/037) : on ne lie
                # un savoir que sous une compétence retenue au scénario.
                comp = competence_de_connaissance(connaissance_id)
                if comp not in competences_retenues_au_scenario_de_seance(seance_id):
                    return SeanceConnaissanceController._rendre(
                        request, seance_id, competence_id,
                        message_garde=("Compétence hors périmètre : retenez-la "
                                       "d'abord au scénario (cochez ses critères)."))
                lier(seance_id, connaissance_id)
            # Les savoirs ouvrants conditionnent la publication de la séquence.
            recalculer_statut_sequence(seance["sequence_id"])
        return SeanceConnaissanceController._rendre(request, seance_id, competence_id)

    @staticmethod
    def niveau(request: Request) -> Response:
        seance_id = _parse_id(request.route("id"))
        seance = get_seance_by_id(seance_id) if seance_id is not None else None
        if seance_id is None or seance is None:
            return BaseController.not_found()
        connaissance_id = _parse_id(request.form("connaissance", ""))
        competence_id = _parse_id(request.form("competence", ""))
        niveau = _parse_id(request.form("niveau", ""))  # None si vide → efface
        if connaissance_id is not None:
            maj_niveau_cible(seance_id, connaissance_id, niveau)
            recalculer_statut_sequence(seance["sequence_id"])
        return SeanceConnaissanceController._rendre(request, seance_id, competence_id)

    @staticmethod
    def statut(request: Request) -> Response:
        seance_id = _parse_id(request.route("id"))
        seance = get_seance_by_id(seance_id) if seance_id is not None else None
        if seance_id is None or seance is None:
            return BaseController.not_found()
        connaissance_id = _parse_id(request.form("connaissance", ""))
        competence_id = _parse_id(request.form("competence", ""))
        statut_val = (request.form("statut", "") or "").strip()
        if statut_val not in STATUT_LABELS:
            statut_val = None  # valeur vide ou inconnue → efface
        if connaissance_id is not None:
            maj_statut(seance_id, connaissance_id, statut_val)
            recalculer_statut_sequence(seance["sequence_id"])
        return SeanceConnaissanceController._rendre(request, seance_id, competence_id)
