# pyright: strict
"""Espace élève — « Mon sequence » (lecture seule).

L'élève **connecté** consulte ses sequence affectés et son avancement par seance.
Route protégée par la permission `espace_eleve.voir` (rôle `eleve`) ; les données
sont filtrées par le compte (`eleve.UserId`), donc chacun ne voit que les siennes.
Un compte non rattaché à un élève voit un message explicite (pas une erreur).
"""
from __future__ import annotations

from core.auth.session import get_authenticated_user_id
from core.http.request import Request
from core.http.response import Response
from core.mvc.controller import BaseController

from mvc.models.ma_sequence_model import ma_sequence


class MaSequenceController:
    @staticmethod
    def index(request: Request) -> Response:
        """« Mon sequence » de l'élève connecté (`GET /ma-sequence`)."""
        user_id = get_authenticated_user_id(request)
        data = ma_sequence(user_id) if user_id is not None else None
        return BaseController.render(
            "app/ma_sequence/index.html",
            context={"data": data},
            request=request,
        )
