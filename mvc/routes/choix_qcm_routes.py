# pyright: strict
"""Routes du contrôleur ChoixQCMController (ADR-068)."""
from core.http.router import Router
from mvc.controllers.choix_qcm_controller import ChoixQCMController


def register_choix_qcm_routes(router: Router) -> None:
    # Routes protégées par défaut. Pour un test local sans authentification :
    #   with router.group("/choix_qcm", public=True, csrf=False) as g:
    with router.group("/choix_qcm") as g:
        g.add("GET", "", ChoixQCMController.index, name="choix_qcm-index")
        g.add("GET", "/new", ChoixQCMController.new, name="choix_qcm-new")
        g.add("POST", "/create", ChoixQCMController.create, name="choix_qcm-create")
        g.add("GET", "/show/{id}", ChoixQCMController.show, name="choix_qcm-show")
        g.add("GET", "/edit/{id}", ChoixQCMController.edit, name="choix_qcm-edit")
        g.add("POST", "/update/{id}", ChoixQCMController.update, name="choix_qcm-update")
        g.add("POST", "/destroy/{id}", ChoixQCMController.destroy, name="choix_qcm-destroy")
        g.add("POST", "/bulk-delete", ChoixQCMController.bulk_delete, name="choix_qcm-bulk_delete")
        g.add("POST", "/bulk-delete-confirm", ChoixQCMController.bulk_delete_confirm, name="choix_qcm-bulk_delete_confirm")
        g.add("GET", "/export-csv", ChoixQCMController.export_csv, name="choix_qcm-export_csv")
