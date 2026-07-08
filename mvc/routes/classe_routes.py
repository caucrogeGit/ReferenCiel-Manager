# pyright: strict
"""Routes du contrôleur ClasseController (ADR-068)."""
from core.http.router import Router
from mvc.controllers.classe_controller import ClasseController


def register_classe_routes(router: Router) -> None:
    # Routes protégées par défaut. Pour un test local sans authentification :
    #   with router.group("/classe", public=True, csrf=False) as g:
    with router.group("/classe") as g:
        g.add("GET", "", ClasseController.index, name="classe-index")
        g.add("GET", "/new", ClasseController.new, name="classe-new")
        g.add("POST", "/create", ClasseController.create, name="classe-create")
        g.add("GET", "/show/{id}", ClasseController.show, name="classe-show")
        g.add("GET", "/edit/{id}", ClasseController.edit, name="classe-edit")
        g.add("POST", "/update/{id}", ClasseController.update, name="classe-update")
        g.add("POST", "/destroy/{id}", ClasseController.destroy, name="classe-destroy")
        g.add("POST", "/bulk-delete", ClasseController.bulk_delete, name="classe-bulk_delete")
        g.add("POST", "/bulk-delete-confirm", ClasseController.bulk_delete_confirm, name="classe-bulk_delete_confirm")
        g.add("GET", "/export-csv", ClasseController.export_csv, name="classe-export_csv")
