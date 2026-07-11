# pyright: strict
"""Routes de l'espace professeur « Mes classes » (lecture seule).

Protégées par la permission `suivi.voir` (garde posée par `guard_prefix` dans
mvc/routes/__init__.py) : rôles `admin` et `professeur`. Données filtrées par le
compte connecté (`professeur.UserId`).
"""
from core.http.router import Router

from mvc.controllers.mes_classes_controller import MesClassesController


def register_mes_classes_routes(router: Router) -> None:
    with router.group("/mes-classes") as g:
        g.add("GET", "", MesClassesController.index, name="mes_classes-index")
