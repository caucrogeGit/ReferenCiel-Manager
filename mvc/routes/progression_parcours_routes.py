"""Routes du contrôleur ProgressionParcoursController (ADR-068)."""
from core.http.router import Router
from mvc.controllers.progression_parcours_controller import ProgressionParcoursController


def register_progression_parcours_routes(router: Router) -> None:
    # Routes protégées par défaut. Pour un test local sans authentification :
    #   with router.group("/progression_parcours", public=True, csrf=False) as g:
    with router.group("/progression_parcours") as g:
        g.add("GET", "", ProgressionParcoursController.index, name="progression_parcours-index")
        g.add("GET", "/new", ProgressionParcoursController.new, name="progression_parcours-new")
        g.add("POST", "/create", ProgressionParcoursController.create, name="progression_parcours-create")
        g.add("GET", "/show/{id}", ProgressionParcoursController.show, name="progression_parcours-show")
        g.add("GET", "/edit/{id}", ProgressionParcoursController.edit, name="progression_parcours-edit")
        g.add("POST", "/update/{id}", ProgressionParcoursController.update, name="progression_parcours-update")
        g.add("POST", "/destroy/{id}", ProgressionParcoursController.destroy, name="progression_parcours-destroy")
        g.add("POST", "/bulk-delete", ProgressionParcoursController.bulk_delete, name="progression_parcours-bulk_delete")
        g.add("POST", "/bulk-delete-confirm", ProgressionParcoursController.bulk_delete_confirm, name="progression_parcours-bulk_delete_confirm")
        g.add("GET", "/export-csv", ProgressionParcoursController.export_csv, name="progression_parcours-export_csv")
