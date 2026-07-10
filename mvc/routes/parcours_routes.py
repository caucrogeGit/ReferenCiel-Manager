# pyright: strict
"""Routes du contrôleur ParcoursController (ADR-068)."""
from core.http.router import Router
from mvc.controllers.parcours_controller import ParcoursController


def register_parcours_routes(router: Router) -> None:
    # Routes protégées par défaut. Pour un test local sans authentification :
    #   with router.group("/parcours", public=True, csrf=False) as g:
    with router.group("/parcours") as g:
        g.add("GET", "", ParcoursController.index, name="parcours-index")
        g.add("GET", "/new", ParcoursController.new, name="parcours-new")
        g.add("POST", "/create", ParcoursController.create, name="parcours-create")
        g.add("GET", "/show/{id}", ParcoursController.show, name="parcours-show")
        g.add("GET", "/edit/{id}", ParcoursController.edit, name="parcours-edit")
        g.add("POST", "/update/{id}", ParcoursController.update, name="parcours-update")
        g.add("POST", "/destroy/{id}", ParcoursController.destroy, name="parcours-destroy")
        g.add("POST", "/bulk-delete", ParcoursController.bulk_delete, name="parcours-bulk_delete")
        g.add("POST", "/bulk-delete-confirm", ParcoursController.bulk_delete_confirm, name="parcours-bulk_delete_confirm")
        g.add("GET", "/export-csv", ParcoursController.export_csv, name="parcours-export_csv")
