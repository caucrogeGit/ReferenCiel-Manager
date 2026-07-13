"""Routes du contrôleur CritereObservableController (ADR-068)."""
from core.http.router import Router
from mvc.controllers.critere_observable_controller import CritereObservableController


def register_critere_observable_routes(router: Router) -> None:
    # Routes protégées par défaut. Pour un test local sans authentification :
    #   with router.group("/critere_observable", public=True, csrf=False) as g:
    with router.group("/critere_observable") as g:
        g.add("GET", "", CritereObservableController.index, name="critere_observable-index")
        g.add("GET", "/new", CritereObservableController.new, name="critere_observable-new")
        g.add("POST", "/create", CritereObservableController.create, name="critere_observable-create")
        g.add("GET", "/show/{id}", CritereObservableController.show, name="critere_observable-show")
        g.add("GET", "/edit/{id}", CritereObservableController.edit, name="critere_observable-edit")
        g.add("POST", "/update/{id}", CritereObservableController.update, name="critere_observable-update")
        g.add("POST", "/destroy/{id}", CritereObservableController.destroy, name="critere_observable-destroy")
        g.add("POST", "/bulk-delete", CritereObservableController.bulk_delete, name="critere_observable-bulk_delete")
        g.add("POST", "/bulk-delete-confirm", CritereObservableController.bulk_delete_confirm, name="critere_observable-bulk_delete_confirm")
        g.add("GET", "/export-csv", CritereObservableController.export_csv, name="critere_observable-export_csv")
