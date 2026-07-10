# pyright: strict
"""Routes du contrôleur ProgressionPalierController (ADR-068)."""
from core.http.router import Router
from mvc.controllers.progression_palier_controller import ProgressionPalierController


def register_progression_palier_routes(router: Router) -> None:
    # Routes protégées par défaut. Pour un test local sans authentification :
    #   with router.group("/progression_palier", public=True, csrf=False) as g:
    with router.group("/progression_palier") as g:
        g.add("GET", "", ProgressionPalierController.index, name="progression_palier-index")
        g.add("GET", "/new", ProgressionPalierController.new, name="progression_palier-new")
        g.add("POST", "/create", ProgressionPalierController.create, name="progression_palier-create")
        g.add("GET", "/show/{id}", ProgressionPalierController.show, name="progression_palier-show")
        g.add("GET", "/edit/{id}", ProgressionPalierController.edit, name="progression_palier-edit")
        g.add("POST", "/update/{id}", ProgressionPalierController.update, name="progression_palier-update")
        g.add("POST", "/destroy/{id}", ProgressionPalierController.destroy, name="progression_palier-destroy")
        g.add("POST", "/bulk-delete", ProgressionPalierController.bulk_delete, name="progression_palier-bulk_delete")
        g.add("POST", "/bulk-delete-confirm", ProgressionPalierController.bulk_delete_confirm, name="progression_palier-bulk_delete_confirm")
        g.add("GET", "/export-csv", ProgressionPalierController.export_csv, name="progression_palier-export_csv")
