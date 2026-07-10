# pyright: strict
"""Routes du contrôleur ItemCocheController (ADR-068)."""
from core.http.router import Router
from mvc.controllers.item_coche_controller import ItemCocheController


def register_item_coche_routes(router: Router) -> None:
    # Routes protégées par défaut. Pour un test local sans authentification :
    #   with router.group("/item_coche", public=True, csrf=False) as g:
    with router.group("/item_coche") as g:
        g.add("GET", "", ItemCocheController.index, name="item_coche-index")
        g.add("GET", "/new", ItemCocheController.new, name="item_coche-new")
        g.add("POST", "/create", ItemCocheController.create, name="item_coche-create")
        g.add("GET", "/show/{id}", ItemCocheController.show, name="item_coche-show")
        g.add("GET", "/edit/{id}", ItemCocheController.edit, name="item_coche-edit")
        g.add("POST", "/update/{id}", ItemCocheController.update, name="item_coche-update")
        g.add("POST", "/destroy/{id}", ItemCocheController.destroy, name="item_coche-destroy")
        g.add("POST", "/bulk-delete", ItemCocheController.bulk_delete, name="item_coche-bulk_delete")
        g.add("POST", "/bulk-delete-confirm", ItemCocheController.bulk_delete_confirm, name="item_coche-bulk_delete_confirm")
        g.add("GET", "/export-csv", ItemCocheController.export_csv, name="item_coche-export_csv")
