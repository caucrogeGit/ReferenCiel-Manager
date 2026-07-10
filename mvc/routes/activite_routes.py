# pyright: strict
"""Routes du contrôleur ActiviteController (ADR-068)."""
from core.http.router import Router
from mvc.controllers.activite_controller import ActiviteController


def register_activite_routes(router: Router) -> None:
    # Routes protégées par défaut. Pour un test local sans authentification :
    #   with router.group("/activite", public=True, csrf=False) as g:
    with router.group("/activite") as g:
        g.add("GET", "", ActiviteController.index, name="activite-index")
        g.add("GET", "/new", ActiviteController.new, name="activite-new")
        g.add("POST", "/create", ActiviteController.create, name="activite-create")
        g.add("GET", "/show/{id}", ActiviteController.show, name="activite-show")
        g.add("GET", "/edit/{id}", ActiviteController.edit, name="activite-edit")
        g.add("POST", "/update/{id}", ActiviteController.update, name="activite-update")
        g.add("POST", "/destroy/{id}", ActiviteController.destroy, name="activite-destroy")
        g.add("POST", "/bulk-delete", ActiviteController.bulk_delete, name="activite-bulk_delete")
        g.add("POST", "/bulk-delete-confirm", ActiviteController.bulk_delete_confirm, name="activite-bulk_delete_confirm")
        g.add("GET", "/export-csv", ActiviteController.export_csv, name="activite-export_csv")
