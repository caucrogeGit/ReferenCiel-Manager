"""Éditeur tunnel de la séance (ADR-032, miroir de l'éditeur séquence).

Phase A. On ne quitte jamais la page : navigation d'étape et auto-save via HTMX
(toast hors-bande). L'étape « Compétences observées » (sélection parmi la liaison
du scénario appairé) est câblée en A2.
"""

from core.http.request import Request
from core.http.response import Response
from core.mvc.controller import BaseController

from mvc.helpers.htmx import est_htmx
from mvc.services.seance_tunnel import borner_etape, navigation, parse_id, steps
from mvc.models.seance_model import get_seance_by_id, update_fiche


def _contexte_editeur(seance: dict, etape: str) -> dict:
    """Contexte complet de l'éditeur (coquille + étape active)."""
    sid = seance["Id"]
    # A1 : la sélection des compétences observées arrive en A2 ; 0 pour l'instant.
    nb_competences = 0
    context = {
        "seance": seance,
        "base_url": f"/seance/editeur/{sid}",
        "steps": steps(seance, nb_competences),
    }
    context.update(navigation(etape))
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
