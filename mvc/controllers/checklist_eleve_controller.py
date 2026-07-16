# pyright: strict
"""Espace élève v2 — cocher la checklist d'une séance.

Route gardée par `espace_eleve.voir` (préfixe `/mon-parcours`) ; le modèle vérifie
en plus l'appartenance de la séance au compte à chaque appel (séance d'autrui → 404).
"""
from __future__ import annotations

from core.auth.session import get_authenticated_user_id
from core.http.request import Request
from core.http.response import Response
from core.mvc.controller import BaseController
from core.security.session import get_flash, get_session_id

from mvc.models.checklist_eleve_model import enregistrer_coches, get_checklist


class ChecklistEleveController:
    @staticmethod
    def show(request: Request) -> Response:
        """La checklist à cocher (`GET /mon-parcours/checklist/<progression_seance_id>`)."""
        user_id = get_authenticated_user_id(request)
        pp_id = int(request.route("id") or "0")
        data = get_checklist(pp_id, user_id) if user_id is not None else None
        if data is None:
            return BaseController.not_found()
        return BaseController.render(
            "app/mon_parcours/checklist.html",
            context={"checklist": data, "flash": get_flash(get_session_id(request))},
            request=request,
        )

    @staticmethod
    def submit(request: Request) -> Response:
        """Enregistre le cochage (`POST /mon-parcours/checklist/<progression_seance_id>`)."""
        user_id = get_authenticated_user_id(request)
        pp_id = int(request.route("id") or "0")
        data = get_checklist(pp_id, user_id) if user_id is not None else None
        if data is None or user_id is None:
            return BaseController.not_found()

        coches: set[int] = set()
        for section in data["sections"]:
            for item in section["items"]:
                iid = int(item["id"])
                if request.form(f"item_{iid}", ""):
                    coches.add(iid)

        resultat = enregistrer_coches(pp_id, user_id, coches)
        if resultat is None:
            return BaseController.not_found()
        message = f"Checklist enregistrée : {resultat['coches']} / {resultat['items']} items cochés."
        return BaseController.redirect_with_flash(request, "/mon-parcours", message, "success")
