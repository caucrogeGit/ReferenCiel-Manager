# pyright: strict
"""Suivi professeur (ticket 20) : tableau de bord **lecture seule** de la progression.

Liste des affectations, puis détail d'une affectation (chaque élève et son avancement
par palier, pour repérer les bloqués / en avance / à évaluer). Route protégée.
"""
from __future__ import annotations

from core.http.request import Request
from core.http.response import Response
from core.mvc.controller import BaseController

from mvc.models.suivi_model import get_affectation, list_affectations, suivi_eleves


class SuiviController:
    @staticmethod
    def index(request: Request) -> Response:
        """Liste des affectations à suivre (`GET /suivi`)."""
        return BaseController.render(
            "suivi/index.html",
            context={"affectations": list_affectations()},
            request=request,
        )

    @staticmethod
    def show(request: Request) -> Response:
        """Suivi d'une affectation : les élèves et leur avancement (`GET /suivi/<id>`)."""
        affectation_id = int(request.route("id") or "0")
        affectation = get_affectation(affectation_id)
        if affectation is None:
            return BaseController.not_found()
        return BaseController.render(
            "suivi/show.html",
            context={"affectation": affectation, "eleves": suivi_eleves(affectation_id)},
            request=request,
        )
