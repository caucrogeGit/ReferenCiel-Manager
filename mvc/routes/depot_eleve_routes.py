# pyright: strict
"""Routes du contrôleur DepotEleveController (ADR-068)."""
from core.http.router import Router
from mvc.controllers.depot_eleve_controller import DepotEleveController


def register_depot_eleve_routes(router: Router) -> None:
    # Routes protégées par défaut. Pour un test local sans authentification :
    #   with router.group("/depot_eleve", public=True, csrf=False) as g:
    with router.group("/depot_eleve") as g:
        g.add("GET", "", DepotEleveController.index, name="depot_eleve-index")
        g.add("GET", "/new", DepotEleveController.new, name="depot_eleve-new")
        g.add("POST", "/create", DepotEleveController.create, name="depot_eleve-create")
        g.add("GET", "/show/{id}", DepotEleveController.show, name="depot_eleve-show")
        g.add("GET", "/edit/{id}", DepotEleveController.edit, name="depot_eleve-edit")
        g.add("POST", "/update/{id}", DepotEleveController.update, name="depot_eleve-update")
        g.add("POST", "/destroy/{id}", DepotEleveController.destroy, name="depot_eleve-destroy")
        g.add("POST", "/bulk-delete", DepotEleveController.bulk_delete, name="depot_eleve-bulk_delete")
        g.add("POST", "/bulk-delete-confirm", DepotEleveController.bulk_delete_confirm, name="depot_eleve-bulk_delete_confirm")
        g.add("GET", "/export-csv", DepotEleveController.export_csv, name="depot_eleve-export_csv")
