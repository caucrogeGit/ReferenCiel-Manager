# pyright: strict
"""Espace élève v2 — passer un QCM.

Affiche le QCM d'une séance de l'élève connecté, puis enregistre sa tentative. La
route est gardée par `espace_eleve.voir` (préfixe `/mon-parcours`) ; en plus, le
modèle vérifie l'**appartenance** de la séance au compte à chaque appel — un id de
séance d'un autre élève renvoie 404, jamais les données d'autrui.
"""
from __future__ import annotations

from core.auth.session import get_authenticated_user_id
from core.http.request import Request
from core.http.response import Response
from core.mvc.controller import BaseController
from core.security.session import get_flash, get_session_id

from mvc.models.passer_qcm_model import enregistrer_tentative, get_qcm_a_passer


class PasserQcmController:
    @staticmethod
    def show(request: Request) -> Response:
        """Le QCM à passer (`GET /mon-parcours/qcm/<progression_seance_id>`)."""
        user_id = get_authenticated_user_id(request)
        pp_id = int(request.route("id") or "0")
        data = get_qcm_a_passer(pp_id, user_id) if user_id is not None else None
        if data is None:
            return BaseController.not_found()
        return BaseController.render(
            "app/mon_parcours/qcm.html",
            context={"qcm": data, "flash": get_flash(get_session_id(request))},
            request=request,
        )

    @staticmethod
    def submit(request: Request) -> Response:
        """Enregistre la tentative (`POST /mon-parcours/qcm/<progression_seance_id>`)."""
        user_id = get_authenticated_user_id(request)
        pp_id = int(request.route("id") or "0")
        data = get_qcm_a_passer(pp_id, user_id) if user_id is not None else None
        if data is None or user_id is None:
            return BaseController.not_found()

        reponses: dict[int, int] = {}
        for question in data["questions"]:
            qid = int(question["id"])
            raw = request.form(f"question_{qid}", "")
            if raw.isdigit():
                reponses[qid] = int(raw)

        resultat = enregistrer_tentative(pp_id, user_id, reponses)
        if resultat is None:
            return BaseController.not_found()

        if resultat["validee"]:
            message = f"Bravo, séance validée ! Score : {resultat['score']} %."
            niveau = "success"
        else:
            message = (
                f"Tentative enregistrée. Score : {resultat['score']} % "
                f"({resultat['total']} questions). Vous pouvez retenter."
            )
            niveau = "info"
        return BaseController.redirect_with_flash(request, "/mon-parcours", message, niveau)
