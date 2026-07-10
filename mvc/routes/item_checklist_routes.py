# pyright: strict
"""Routes du contrôleur ItemChecklistController (ADR-068)."""
from core.http.router import Router
from mvc.controllers.item_checklist_controller import ItemChecklistController


def register_item_checklist_routes(router: Router) -> None:
    # Routes protégées par défaut. Pour un test local sans authentification :
    #   with router.group("/item_checklist", public=True, csrf=False) as g:
    with router.group("/item_checklist") as g:
        g.add("GET", "", ItemChecklistController.index, name="item_checklist-index")
        g.add("GET", "/new", ItemChecklistController.new, name="item_checklist-new")
        g.add("POST", "/create", ItemChecklistController.create, name="item_checklist-create")
        g.add("GET", "/show/{id}", ItemChecklistController.show, name="item_checklist-show")
        g.add("GET", "/edit/{id}", ItemChecklistController.edit, name="item_checklist-edit")
        g.add("POST", "/update/{id}", ItemChecklistController.update, name="item_checklist-update")
        g.add("POST", "/destroy/{id}", ItemChecklistController.destroy, name="item_checklist-destroy")
        g.add("POST", "/bulk-delete", ItemChecklistController.bulk_delete, name="item_checklist-bulk_delete")
        g.add("POST", "/bulk-delete-confirm", ItemChecklistController.bulk_delete_confirm, name="item_checklist-bulk_delete_confirm")
        g.add("GET", "/export-csv", ItemChecklistController.export_csv, name="item_checklist-export_csv")
