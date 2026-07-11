# pyright: strict
"""Espace professeur — « Mes classes » (lecture seule).

Le professeur **connecté** consulte les classes où il est affecté et les élèves
qui y sont inscrits. Route protégée par la permission `suivi.voir` (rôles `admin`
et `professeur`) ; les données sont filtrées par le compte (`professeur.UserId`),
donc chacun ne voit que ses propres classes. Un compte non rattaché à un
professeur voit un message explicite (pas une erreur). Tranche verticale Bloc A
(ticket 07).
"""
from __future__ import annotations

from core.auth.session import get_authenticated_user_id
from core.http.request import Request
from core.http.response import Response
from core.mvc.controller import BaseController

from mvc.models.mes_classes_model import mes_classes


class MesClassesController:
    @staticmethod
    def index(request: Request) -> Response:
        """« Mes classes » du professeur connecté (`GET /mes-classes`)."""
        user_id = get_authenticated_user_id(request)
        data = mes_classes(user_id) if user_id is not None else None
        return BaseController.render(
            "app/mes_classes/index.html",
            context={"data": data},
            request=request,
        )
