"""Routes du contrôleur ProgressionEleveController (ADR-068)."""
from core.http.router import Router
from mvc.controllers.progression_eleve_controller import ProgressionEleveController


def register_progression_eleve_routes(router: Router) -> None:
    # Routes protégées par défaut. Pour un test local sans authentification :
    #   with router.group("/progression_eleve", public=True, csrf=False) as g:
    with router.group("/progression_eleve") as g:
        g.add("GET", "", ProgressionEleveController.index, name="progression_eleve-index")
        g.add("GET", "/new", ProgressionEleveController.new, name="progression_eleve-new")
        g.add("POST", "/create", ProgressionEleveController.create, name="progression_eleve-create")
        g.add("GET", "/show/{id}", ProgressionEleveController.show, name="progression_eleve-show")
        g.add("GET", "/edit/{id}", ProgressionEleveController.edit, name="progression_eleve-edit")
        g.add("POST", "/update/{id}", ProgressionEleveController.update, name="progression_eleve-update")
        g.add("POST", "/destroy/{id}", ProgressionEleveController.destroy, name="progression_eleve-destroy")
        g.add("POST", "/bulk-delete", ProgressionEleveController.bulk_delete, name="progression_eleve-bulk_delete")
        g.add("POST", "/bulk-delete-confirm", ProgressionEleveController.bulk_delete_confirm, name="progression_eleve-bulk_delete_confirm")
        g.add("GET", "/export-csv", ProgressionEleveController.export_csv, name="progression_eleve-export_csv")
