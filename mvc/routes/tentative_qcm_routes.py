# pyright: strict
"""Routes du contrôleur TentativeQCMController (ADR-068)."""
from core.http.router import Router
from mvc.controllers.tentative_qcm_controller import TentativeQCMController


def register_tentative_qcm_routes(router: Router) -> None:
    # Routes protégées par défaut. Pour un test local sans authentification :
    #   with router.group("/tentative_qcm", public=True, csrf=False) as g:
    with router.group("/tentative_qcm") as g:
        g.add("GET", "", TentativeQCMController.index, name="tentative_qcm-index")
        g.add("GET", "/new", TentativeQCMController.new, name="tentative_qcm-new")
        g.add("POST", "/create", TentativeQCMController.create, name="tentative_qcm-create")
        g.add("GET", "/show/{id}", TentativeQCMController.show, name="tentative_qcm-show")
        g.add("GET", "/edit/{id}", TentativeQCMController.edit, name="tentative_qcm-edit")
        g.add("POST", "/update/{id}", TentativeQCMController.update, name="tentative_qcm-update")
        g.add("POST", "/destroy/{id}", TentativeQCMController.destroy, name="tentative_qcm-destroy")
        g.add("POST", "/bulk-delete", TentativeQCMController.bulk_delete, name="tentative_qcm-bulk_delete")
        g.add("POST", "/bulk-delete-confirm", TentativeQCMController.bulk_delete_confirm, name="tentative_qcm-bulk_delete_confirm")
        g.add("GET", "/export-csv", TentativeQCMController.export_csv, name="tentative_qcm-export_csv")
