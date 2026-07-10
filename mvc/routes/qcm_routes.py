# pyright: strict
"""Routes du contrôleur QCMController (ADR-068)."""
from core.http.router import Router
from mvc.controllers.qcm_controller import QCMController


def register_qcm_routes(router: Router) -> None:
    # Routes protégées par défaut. Pour un test local sans authentification :
    #   with router.group("/qcm", public=True, csrf=False) as g:
    with router.group("/qcm") as g:
        g.add("GET", "", QCMController.index, name="qcm-index")
        g.add("GET", "/new", QCMController.new, name="qcm-new")
        g.add("POST", "/create", QCMController.create, name="qcm-create")
        g.add("GET", "/show/{id}", QCMController.show, name="qcm-show")
        g.add("GET", "/edit/{id}", QCMController.edit, name="qcm-edit")
        g.add("POST", "/update/{id}", QCMController.update, name="qcm-update")
        g.add("POST", "/destroy/{id}", QCMController.destroy, name="qcm-destroy")
        g.add("POST", "/bulk-delete", QCMController.bulk_delete, name="qcm-bulk_delete")
        g.add("POST", "/bulk-delete-confirm", QCMController.bulk_delete_confirm, name="qcm-bulk_delete_confirm")
        g.add("GET", "/export-csv", QCMController.export_csv, name="qcm-export_csv")
