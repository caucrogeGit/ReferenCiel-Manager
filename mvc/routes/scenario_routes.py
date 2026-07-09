# pyright: strict
"""Routes du contrôleur ScenarioController (ADR-068)."""
from core.http.router import Router
from mvc.controllers.scenario_controller import ScenarioController


def register_scenario_routes(router: Router) -> None:
    # Routes protégées par défaut. Pour un test local sans authentification :
    #   with router.group("/scenario", public=True, csrf=False) as g:
    with router.group("/scenario") as g:
        g.add("GET", "", ScenarioController.index, name="scenario-index")
        g.add("GET", "/new", ScenarioController.new, name="scenario-new")
        g.add("POST", "/create", ScenarioController.create, name="scenario-create")
        g.add("GET", "/show/{id}", ScenarioController.show, name="scenario-show")
        g.add("GET", "/edit/{id}", ScenarioController.edit, name="scenario-edit")
        g.add("POST", "/update/{id}", ScenarioController.update, name="scenario-update")
        g.add("POST", "/destroy/{id}", ScenarioController.destroy, name="scenario-destroy")
        g.add("POST", "/bulk-delete", ScenarioController.bulk_delete, name="scenario-bulk_delete")
        g.add("POST", "/bulk-delete-confirm", ScenarioController.bulk_delete_confirm, name="scenario-bulk_delete_confirm")
        g.add("GET", "/export-csv", ScenarioController.export_csv, name="scenario-export_csv")
