# pyright: strict
"""Routes du contrôleur ChecklistController (ADR-068)."""
from core.http.router import Router
from mvc.controllers.checklist_controller import ChecklistController


def register_checklist_routes(router: Router) -> None:
    # Routes protégées par défaut. Pour un test local sans authentification :
    #   with router.group("/checklist", public=True, csrf=False) as g:
    with router.group("/checklist") as g:
        g.add("GET", "", ChecklistController.index, name="checklist-index")
        g.add("GET", "/new", ChecklistController.new, name="checklist-new")
        g.add("POST", "/create", ChecklistController.create, name="checklist-create")
        g.add("GET", "/show/{id}", ChecklistController.show, name="checklist-show")
        g.add("GET", "/edit/{id}", ChecklistController.edit, name="checklist-edit")
        g.add("POST", "/update/{id}", ChecklistController.update, name="checklist-update")
        g.add("POST", "/destroy/{id}", ChecklistController.destroy, name="checklist-destroy")
        g.add("POST", "/bulk-delete", ChecklistController.bulk_delete, name="checklist-bulk_delete")
        g.add("POST", "/bulk-delete-confirm", ChecklistController.bulk_delete_confirm, name="checklist-bulk_delete_confirm")
        g.add("GET", "/export-csv", ChecklistController.export_csv, name="checklist-export_csv")
