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
        g.add("POST", "/{id}/contexte", ScenarioEditeurController.enregistrer_contexte, name="scenario_editeur-contexte")
        g.add("POST", "/{id}/referentiel", ScenarioEditeurController.enregistrer_referentiel, name="scenario_editeur-referentiel")
        g.add("POST", "/{id}/liaison", ScenarioEditeurController.enregistrer_liaison, name="scenario_editeur-liaison")
        # Cochage unitaire (tunnel maître-détail, ADR-021). Sert HTMX et le POST
        # sans JS. Gardé par le préfixe /conception -> conception.gerer (routes/__init__.py).
        g.add("POST", "/{id}/activite/basculer", ScenarioEditeurController.basculer_activite, name="scenario_editeur-activite-basculer")
        g.add("POST", "/{id}/critere/basculer", ScenarioEditeurController.basculer_critere, name="scenario_editeur-critere-basculer")
        g.add("POST", "/{id}/ressources", ScenarioEditeurController.uploader_ressource, name="scenario_editeur-ressource-upload")
        g.add("POST", "/{id}/ressources/{rid}/supprimer", ScenarioEditeurController.supprimer_ressource, name="scenario_editeur-ressource-supprimer")
