# pyright: strict
"""Routes de l'atelier référentiel (ADR-018). Gardé par referentiel.gerer (RBAC)."""
from core.http.router import Router

from mvc.controllers.referentiel_atelier_controller import ReferentielAtelierController


def register_referentiel_atelier_routes(router: Router) -> None:
    with router.group("/referentiel") as g:
        g.add("GET", "", ReferentielAtelierController.index, name="referentiel_atelier-index")
        g.add("GET", "/{id}", ReferentielAtelierController.atelier, name="referentiel_atelier-atelier")
