# pyright: strict
"""Routes du contrôleur ProgressionSeanceController (ADR-068)."""
from core.http.router import Router
from mvc.controllers.progression_seance_controller import ProgressionSeanceController


def register_progression_seance_routes(router: Router) -> None:
    # Routes protégées par défaut. Pour un test local sans authentification :
    #   with router.group("/progression_seance", public=True, csrf=False) as g:
    with router.group("/progression_seance") as g:
        g.add("GET", "", ProgressionSeanceController.index, name="progression_seance-index")
        g.add("GET", "/new", ProgressionSeanceController.new, name="progression_seance-new")
        g.add("POST", "/create", ProgressionSeanceController.create, name="progression_seance-create")
        g.add("GET", "/show/{id}", ProgressionSeanceController.show, name="progression_seance-show")
        g.add("GET", "/edit/{id}", ProgressionSeanceController.edit, name="progression_seance-edit")
        g.add("POST", "/update/{id}", ProgressionSeanceController.update, name="progression_seance-update")
        g.add("POST", "/destroy/{id}", ProgressionSeanceController.destroy, name="progression_seance-destroy")
        g.add("POST", "/bulk-delete", ProgressionSeanceController.bulk_delete, name="progression_seance-bulk_delete")
        g.add("POST", "/bulk-delete-confirm", ProgressionSeanceController.bulk_delete_confirm, name="progression_seance-bulk_delete_confirm")
        g.add("GET", "/export-csv", ProgressionSeanceController.export_csv, name="progression_seance-export_csv")
