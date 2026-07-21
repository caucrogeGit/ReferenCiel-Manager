"""Éditeur tunnel de la séance (ADR-032, miroir de l'éditeur séquence).

On ne quitte jamais la page : navigation d'étape et auto-save via HTMX (toast
hors-bande). L'étape « Compétences observées » propose une sélection maître-détail
PARMI la liaison du scénario appairé (cascade sans double saisie).
"""

from core.http.request import Request
from core.http.response import Response
from core.mvc.controller import BaseController

from mvc.helpers.htmx import est_htmx
from mvc.services.seance_tunnel import borner_etape, navigation, parse_id, steps
from mvc.models.seance_model import get_seance_by_id, update_fiche
from mvc.models.seance_competence_model import (
    ROLE_LABELS,
    get_scenario_id_for_seance,
    get_arbre_liaison,
    get_competences_observees,
    get_criteres_observes,
    basculer_competence,
    maj_role,
    basculer_critere,
)
from mvc.models.element_seance_model import (
    TYPES,
    TYPE_LABELS,
    get_elements,
    get_element,
    ajouter as ajouter_element_db,
    maj as maj_element_db,
    supprimer as supprimer_element_db,
    deplacer as deplacer_element_db,
)

_ROLES = [(v, ROLE_LABELS[v]) for v in ROLE_LABELS]
_TYPES = [(t, TYPE_LABELS[t]) for t in TYPES]


def _query(request, name, default=""):
    values = request.params.get(name, [default])
    return values[0] if values else default


def contexte_competences(seance_id, competence_id=None):
    """Contexte de l'étape Compétences observées (maître-détail scopé scénario)."""
    scenario_id = get_scenario_id_for_seance(seance_id)
    groupes = get_arbre_liaison(scenario_id) if scenario_id is not None else []
    if not groupes:
        return {
            "seance_id": seance_id,
            "liaison_absente": True,
            "groupes": [],
            "competences_observees": {},
            "criteres_observes": set(),
            "competence_id": None,
            "roles": _ROLES,
        }
    if competence_id is None:
        competence_id = groupes[0]["Id"]
    return {
        "seance_id": seance_id,
        "liaison_absente": False,
        "groupes": groupes,
        "competences_observees": get_competences_observees(seance_id),
        "criteres_observes": get_criteres_observes(seance_id),
        "competence_id": competence_id,
        "roles": _ROLES,
    }


def contexte_deroule(seance_id):
    """Contexte de l'étape Déroulé (liste ordonnée des éléments + types)."""
    return {
        "seance_id": seance_id,
        "elements": get_elements(seance_id),
        "types": _TYPES,
        "type_labels": TYPE_LABELS,
    }


def _contexte_editeur(seance: dict, etape: str) -> dict:
    """Contexte complet de l'éditeur (coquille + étape active)."""
    sid = seance["Id"]
    nb_competences = len(get_competences_observees(sid))
    nb_elements = len(get_elements(sid))
    context = {
        "seance": seance,
        "base_url": f"/seance/editeur/{sid}",
        "steps": steps(seance, nb_competences, nb_elements),
    }
    context.update(navigation(etape))
    context.update(contexte_competences(sid))
    context.update(contexte_deroule(sid))
    return context


class SeanceEditeurController(BaseController):

    @staticmethod
    def editeur(request: Request) -> Response:
        sid = parse_id(request.route("id"))
        if sid is None:
            return BaseController.not_found()
        seance = get_seance_by_id(sid)
        if seance is None:
            return BaseController.not_found()
        etape = borner_etape(request.query("etape", "fiche"))
        context = _contexte_editeur(seance, etape)
        template = "app/seance_editeur/_corps.html" if est_htmx(request) else "app/seance_editeur/editeur.html"
        return BaseController.render(template, context=context, request=request)

    @staticmethod
    def enregistrer_fiche(request: Request) -> Response:
        sid = parse_id(request.route("id"))
        if sid is None or get_seance_by_id(sid) is None:
            return BaseController.not_found()
        data = {
            "ordre": parse_id(request.form("ordre", "")) or 1,
            "titre": (request.form("titre", "") or "").strip(),
            "theme": (request.form("theme", "") or "").strip() or None,
            "production_attendue": (request.form("production_attendue", "") or "").strip() or None,
            "objectif_operationnel": (request.form("objectif_operationnel", "") or "").strip() or None,
            "consigne_generale": (request.form("consigne_generale", "") or "").strip() or None,
            "duree_estimee_minutes": parse_id(request.form("duree_estimee_minutes", "")),
            "modalite_pedagogique": (request.form("modalite_pedagogique", "") or "").strip() or None,
            "condition_realisation": (request.form("condition_realisation", "") or "").strip() or None,
            "condition_validation": (request.form("condition_validation", "") or "").strip() or None,
            "remediation": (request.form("remediation", "") or "").strip() or None,
        }
        update_fiche(sid, data)
        if est_htmx(request):
            return BaseController.render(
                "app/seance_editeur/_sauvegarde_oob.html", context={}, request=request
            )
        return BaseController.redirect(f"/seance/editeur/{sid}", request=request)

    # ── Étape Compétences observées (maître-détail, ADR-032 A2) ──────────────

    @staticmethod
    def _rendre_competences(request: Request, sid: int, competence_id) -> Response:
        if not est_htmx(request):
            return BaseController.redirect(
                f"/seance/editeur/{sid}?etape=competences", request=request
            )
        return BaseController.render(
            "app/seance_editeur/_competences.html",
            context=contexte_competences(sid, competence_id),
            request=request,
        )

    @staticmethod
    def afficher_competences(request: Request) -> Response:
        sid = parse_id(request.route("id"))
        if sid is None or get_seance_by_id(sid) is None:
            return BaseController.not_found()
        competence_id = parse_id(_query(request, "competence"))
        return SeanceEditeurController._rendre_competences(request, sid, competence_id)

    @staticmethod
    def basculer_competence(request: Request) -> Response:
        sid = parse_id(request.route("id"))
        if sid is None or get_seance_by_id(sid) is None:
            return BaseController.not_found()
        competence_id = parse_id(request.form("competence", ""))
        if competence_id is not None:
            basculer_competence(sid, competence_id, request.form("role", "travaillee"))
        return SeanceEditeurController._rendre_competences(request, sid, competence_id)

    @staticmethod
    def changer_role(request: Request) -> Response:
        sid = parse_id(request.route("id"))
        if sid is None or get_seance_by_id(sid) is None:
            return BaseController.not_found()
        competence_id = parse_id(request.form("competence", ""))
        if competence_id is not None:
            maj_role(sid, competence_id, (request.form("role", "") or "").strip())
        return SeanceEditeurController._rendre_competences(request, sid, competence_id)

    @staticmethod
    def basculer_critere(request: Request) -> Response:
        sid = parse_id(request.route("id"))
        if sid is None or get_seance_by_id(sid) is None:
            return BaseController.not_found()
        competence_id = parse_id(request.form("competence", ""))
        critere_id = parse_id(request.form("critere", ""))
        if critere_id is not None:
            basculer_critere(sid, critere_id)
        return SeanceEditeurController._rendre_competences(request, sid, competence_id)

    # ── Étape Déroulé : éléments ordonnés (ADR-032 phase B) ──────────────────

    @staticmethod
    def _rendre_deroule(request: Request, sid: int) -> Response:
        if not est_htmx(request):
            return BaseController.redirect(f"/seance/editeur/{sid}?etape=deroule", request=request)
        return BaseController.render(
            "app/seance_editeur/_elements.html", context=contexte_deroule(sid), request=request
        )

    @staticmethod
    def _lire_element(request: Request) -> dict:
        return {
            "titre": (request.form("titre", "") or "").strip(),
            "contenu": (request.form("contenu", "") or "").strip() or None,
            "duree": parse_id(request.form("duree_minutes", "")),
            "obligatoire": request.form("obligatoire", "") != "",
            "role": (request.form("role_pedagogique", "") or "").strip() or None,
        }

    @staticmethod
    def ajouter_element(request: Request) -> Response:
        sid = parse_id(request.route("id"))
        if sid is None or get_seance_by_id(sid) is None:
            return BaseController.not_found()
        type_ = (request.form("type", "") or "").strip()
        d = SeanceEditeurController._lire_element(request)
        if type_ in TYPES and d["titre"]:
            ajouter_element_db(sid, type_, d["titre"], d["contenu"], d["duree"], d["obligatoire"], d["role"])
        return SeanceEditeurController._rendre_deroule(request, sid)

    @staticmethod
    def maj_element(request: Request) -> Response:
        eid = parse_id(request.route("eid"))
        if eid is None:
            return BaseController.not_found()
        element = get_element(eid)
        if element is None:
            return BaseController.not_found()
        d = SeanceEditeurController._lire_element(request)
        if d["titre"]:
            maj_element_db(eid, d["titre"], d["contenu"], d["duree"], d["obligatoire"], d["role"])
        return SeanceEditeurController._rendre_deroule(request, element["seance_id"])

    @staticmethod
    def supprimer_element(request: Request) -> Response:
        eid = parse_id(request.route("eid"))
        if eid is None:
            return BaseController.not_found()
        element = get_element(eid)
        if element is None:
            return BaseController.not_found()
        seance_id = element["seance_id"]
        supprimer_element_db(eid)
        return SeanceEditeurController._rendre_deroule(request, seance_id)

    @staticmethod
    def deplacer_element(request: Request) -> Response:
        eid = parse_id(request.route("eid"))
        if eid is None:
            return BaseController.not_found()
        element = get_element(eid)
        if element is None:
            return BaseController.not_found()
        sens = (request.form("sens", "") or "").strip()
        if sens in ("haut", "bas"):
            deplacer_element_db(eid, sens)
        return SeanceEditeurController._rendre_deroule(request, element["seance_id"])
