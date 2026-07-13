"""Routes du contrôleur FormationController (ADR-068)."""
from core.http.router import Router
from mvc.controllers.formation_controller import FormationController


def register_formation_routes(router: Router) -> None:
    # Routes protégées par défaut. Pour un test local sans authentification :
    #   with router.group("/formation", public=True, csrf=False) as g:
    with router.group("/formation") as g:
        g.add("GET", "", FormationController.index, name="formation-index")
        g.add("GET", "/new", FormationController.new, name="formation-new")
        g.add("POST", "/create", FormationController.create, name="formation-create")
        g.add("GET", "/show/{id}", FormationController.show, name="formation-show")
        g.add("GET", "/edit/{id}", FormationController.edit, name="formation-edit")
        g.add("POST", "/update/{id}", FormationController.update, name="formation-update")
        g.add("POST", "/destroy/{id}", FormationController.destroy, name="formation-destroy")
        g.add("POST", "/bulk-delete", FormationController.bulk_delete, name="formation-bulk_delete")
        g.add("POST", "/bulk-delete-confirm", FormationController.bulk_delete_confirm, name="formation-bulk_delete_confirm")
        g.add("GET", "/export-csv", FormationController.export_csv, name="formation-export_csv")
