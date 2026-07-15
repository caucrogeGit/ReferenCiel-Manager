"""Routes du contrôleur PalierController (ADR-068)."""
from core.http.router import Router
from mvc.controllers.palier_controller import PalierController


def register_palier_routes(router: Router) -> None:
    # Routes protégées par défaut. Pour un test local sans authentification :
    #   with router.group("/palier", public=True, csrf=False) as g:
    with router.group("/palier") as g:
        g.add("GET", "", PalierController.index, name="palier-index")
        g.add("GET", "/new", PalierController.new, name="palier-new")
        g.add("POST", "/create", PalierController.create, name="palier-create")
        g.add("GET", "/show/{id}", PalierController.show, name="palier-show")
        g.add("GET", "/edit/{id}", PalierController.edit, name="palier-edit")
        g.add("POST", "/update/{id}", PalierController.update, name="palier-update")
        g.add("POST", "/destroy/{id}", PalierController.destroy, name="palier-destroy")
        g.add("POST", "/bulk-delete", PalierController.bulk_delete, name="palier-bulk_delete")
        g.add("POST", "/bulk-delete-confirm", PalierController.bulk_delete_confirm, name="palier-bulk_delete_confirm")
        g.add("GET", "/export-csv", PalierController.export_csv, name="palier-export_csv")
