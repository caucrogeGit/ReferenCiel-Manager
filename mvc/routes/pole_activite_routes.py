"""Routes du contrôleur PoleActiviteController (ADR-068)."""
from core.http.router import Router
from mvc.controllers.pole_activite_controller import PoleActiviteController


def register_pole_activite_routes(router: Router) -> None:
    # Routes protégées par défaut. Pour un test local sans authentification :
    #   with router.group("/pole_activite", public=True, csrf=False) as g:
    with router.group("/pole_activite") as g:
        g.add("GET", "", PoleActiviteController.index, name="pole_activite-index")
        g.add("GET", "/new", PoleActiviteController.new, name="pole_activite-new")
        g.add("POST", "/create", PoleActiviteController.create, name="pole_activite-create")
        g.add("GET", "/show/{id}", PoleActiviteController.show, name="pole_activite-show")
        g.add("GET", "/edit/{id}", PoleActiviteController.edit, name="pole_activite-edit")
        g.add("POST", "/update/{id}", PoleActiviteController.update, name="pole_activite-update")
        g.add("POST", "/destroy/{id}", PoleActiviteController.destroy, name="pole_activite-destroy")
        g.add("POST", "/bulk-delete", PoleActiviteController.bulk_delete, name="pole_activite-bulk_delete")
        g.add("POST", "/bulk-delete-confirm", PoleActiviteController.bulk_delete_confirm, name="pole_activite-bulk_delete_confirm")
        g.add("GET", "/export-csv", PoleActiviteController.export_csv, name="pole_activite-export_csv")
