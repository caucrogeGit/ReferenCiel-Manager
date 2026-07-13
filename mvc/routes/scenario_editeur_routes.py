# pyright: strict
"""Routes de l'éditeur de scénario (ADR-019). Gardé par conception.gerer (RBAC)."""
from core.http.router import Router

from mvc.controllers.scenario_editeur_controller import ScenarioEditeurController


def register_scenario_editeur_routes(router: Router) -> None:
    with router.group("/conception/scenario") as g:
        g.add("GET", "", ScenarioEditeurController.index, name="scenario_editeur-index")
        g.add("POST", "/nouveau", ScenarioEditeurController.nouveau, name="scenario_editeur-nouveau")
        g.add("GET", "/{id}", ScenarioEditeurController.editeur, name="scenario_editeur-editeur")
        g.add("POST", "/{id}/titre", ScenarioEditeurController.enregistrer_titre, name="scenario_editeur-titre")
