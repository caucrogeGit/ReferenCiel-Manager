# pyright: strict
"""Routes du contrôleur ReponseQCMController (ADR-068)."""
from core.http.router import Router
from mvc.controllers.reponse_qcm_controller import ReponseQCMController


def register_reponse_qcm_routes(router: Router) -> None:
    # Routes protégées par défaut. Pour un test local sans authentification :
    #   with router.group("/reponse_qcm", public=True, csrf=False) as g:
    with router.group("/reponse_qcm") as g:
        g.add("GET", "", ReponseQCMController.index, name="reponse_qcm-index")
        g.add("GET", "/new", ReponseQCMController.new, name="reponse_qcm-new")
        g.add("POST", "/create", ReponseQCMController.create, name="reponse_qcm-create")
        g.add("GET", "/show/{id}", ReponseQCMController.show, name="reponse_qcm-show")
        g.add("GET", "/edit/{id}", ReponseQCMController.edit, name="reponse_qcm-edit")
        g.add("POST", "/update/{id}", ReponseQCMController.update, name="reponse_qcm-update")
        g.add("POST", "/destroy/{id}", ReponseQCMController.destroy, name="reponse_qcm-destroy")
        g.add("POST", "/bulk-delete", ReponseQCMController.bulk_delete, name="reponse_qcm-bulk_delete")
        g.add("POST", "/bulk-delete-confirm", ReponseQCMController.bulk_delete_confirm, name="reponse_qcm-bulk_delete_confirm")
        g.add("GET", "/export-csv", ReponseQCMController.export_csv, name="reponse_qcm-export_csv")
