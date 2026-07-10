# pyright: strict
"""Routes du contrôleur QuestionQCMController (ADR-068)."""
from core.http.router import Router
from mvc.controllers.question_qcm_controller import QuestionQCMController


def register_question_qcm_routes(router: Router) -> None:
    # Routes protégées par défaut. Pour un test local sans authentification :
    #   with router.group("/question_qcm", public=True, csrf=False) as g:
    with router.group("/question_qcm") as g:
        g.add("GET", "", QuestionQCMController.index, name="question_qcm-index")
        g.add("GET", "/new", QuestionQCMController.new, name="question_qcm-new")
        g.add("POST", "/create", QuestionQCMController.create, name="question_qcm-create")
        g.add("GET", "/show/{id}", QuestionQCMController.show, name="question_qcm-show")
        g.add("GET", "/edit/{id}", QuestionQCMController.edit, name="question_qcm-edit")
        g.add("POST", "/update/{id}", QuestionQCMController.update, name="question_qcm-update")
        g.add("POST", "/destroy/{id}", QuestionQCMController.destroy, name="question_qcm-destroy")
        g.add("POST", "/bulk-delete", QuestionQCMController.bulk_delete, name="question_qcm-bulk_delete")
        g.add("POST", "/bulk-delete-confirm", QuestionQCMController.bulk_delete_confirm, name="question_qcm-bulk_delete_confirm")
        g.add("GET", "/export-csv", QuestionQCMController.export_csv, name="question_qcm-export_csv")
