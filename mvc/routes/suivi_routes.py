# pyright: strict
"""Routes du suivi professeur (ticket 20) — tableau de bord lecture seule.

Protégées (session requise). RBAC rôle professeur/admin différé (opt-in `rbac`).
"""
from core.http.router import Router
from mvc.controllers.suivi_controller import SuiviController


def register_suivi_routes(router: Router) -> None:
    with router.group("/suivi") as g:
        g.add("GET", "", SuiviController.index, name="suivi-index")
        g.add("GET", "/{id}", SuiviController.show, name="suivi-show")
