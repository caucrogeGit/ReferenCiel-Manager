# pyright: strict
"""Suivi professeur (ticket 20, revu ADR-022) : tableau de bord **lecture seule** de
la progression, organisé **par CLASSE** du professeur connecté.

Liste des classes du prof, puis détail d'une classe (chaque élève et son avancement
par palier, pour repérer les bloqués / en avance / à évaluer). Route protégée.
"""
from __future__ import annotations

from core.auth.session import get_authenticated_user_id
from core.http.request import Request
from core.http.response import Response
from core.mvc.controller import BaseController

from mvc.models.mes_classes_model import get_professeur_by_user
from mvc.models.suivi_model import get_classe, list_classes, suivi_eleves


class SuiviController:
    @staticmethod
    def index(request: Request) -> Response:
        """Liste des classes du professeur à suivre (`GET /suivi`)."""
        user_id = get_authenticated_user_id(request)
        professeur = get_professeur_by_user(user_id) if user_id is not None else None
        classes = list_classes(int(professeur["id"])) if professeur is not None else []
        return BaseController.render(
            "app/suivi/index.html",
            context={"classes": classes},
            request=request,
        )

    @staticmethod
    def show(request: Request) -> Response:
        """Suivi d'une classe : les élèves et leur avancement (`GET /suivi/<id>`)."""
        classe_id = int(request.route("id") or "0")
        classe = get_classe(classe_id)
        if classe is None:
            return BaseController.not_found()
        return BaseController.render(
            "app/suivi/show.html",
            context={"classe": classe, "eleves": suivi_eleves(classe_id)},
            request=request,
        )
