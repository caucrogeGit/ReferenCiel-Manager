# pyright: strict
"""Routes du contrôleur EleveController (ADR-068)."""
from core.http.router import Router
from mvc.controllers.eleve_controller import EleveController


def register_eleve_routes(router: Router) -> None:
    # Routes protégées par défaut. Pour un test local sans authentification :
    #   with router.group("/eleve", public=True, csrf=False) as g:
    with router.group("/eleve") as g:
        g.add("GET", "", EleveController.index, name="eleve-index")
        g.add("GET", "/new", EleveController.new, name="eleve-new")
        g.add("POST", "/create", EleveController.create, name="eleve-create")
        g.add("GET", "/show/{id}", EleveController.show, name="eleve-show")
        g.add("GET", "/edit/{id}", EleveController.edit, name="eleve-edit")
        g.add("POST", "/update/{id}", EleveController.update, name="eleve-update")
        g.add("POST", "/destroy/{id}", EleveController.destroy, name="eleve-destroy")
        g.add("POST", "/bulk-delete", EleveController.bulk_delete, name="eleve-bulk_delete")
        g.add("POST", "/bulk-delete-confirm", EleveController.bulk_delete_confirm, name="eleve-bulk_delete_confirm")
        g.add("GET", "/export-csv", EleveController.export_csv, name="eleve-export_csv")
