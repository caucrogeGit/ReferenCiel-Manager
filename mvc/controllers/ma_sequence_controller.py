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

from mvc.models.ma_sequence_model import (
    get_eleve_by_user,
    get_mon_bilan,
    ma_sequence,
    mes_bilans,
)


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

    @staticmethod
    def bilans(request: Request) -> Response:
        """Bilans publiés de l'élève connecté (`GET /ma-sequence/bilans`)."""
        user_id = get_authenticated_user_id(request)
        eleve = get_eleve_by_user(user_id) if user_id is not None else None
        bilans = mes_bilans(int(eleve["id"])) if eleve is not None else []
        return BaseController.render(
            "app/ma_sequence/bilans.html",
            context={"eleve": eleve, "bilans": bilans},
            request=request,
        )

    @staticmethod
    def bilan(request: Request) -> Response:
        """Lecture d'un bilan publié de l'élève connecté (`GET /ma-sequence/bilan/<id>`).

        Sécurité au niveau ligne : `get_mon_bilan` filtre sur l'élève ET le statut
        publié, donc un compte ne peut pas lire le bilan d'un autre, ni un brouillon."""
        user_id = get_authenticated_user_id(request)
        eleve = get_eleve_by_user(user_id) if user_id is not None else None
        if eleve is None:
            return BaseController.not_found()
        bilan_id = int(request.route("id") or "0")
        bilan = get_mon_bilan(int(eleve["id"]), bilan_id)
        if bilan is None:
            return BaseController.not_found()
        return BaseController.render(
            "app/ma_sequence/bilan.html",
            context={"bilan": bilan},
            request=request,
        )
