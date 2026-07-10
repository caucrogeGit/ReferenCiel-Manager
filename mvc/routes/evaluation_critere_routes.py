# pyright: strict
"""Routes du contrôleur EvaluationCritereController (ADR-068)."""
from core.http.router import Router
from mvc.controllers.evaluation_critere_controller import EvaluationCritereController


def register_evaluation_critere_routes(router: Router) -> None:
    # Routes protégées par défaut. Pour un test local sans authentification :
    #   with router.group("/evaluation_critere", public=True, csrf=False) as g:
    with router.group("/evaluation_critere") as g:
        g.add("GET", "", EvaluationCritereController.index, name="evaluation_critere-index")
        g.add("GET", "/new", EvaluationCritereController.new, name="evaluation_critere-new")
        g.add("POST", "/create", EvaluationCritereController.create, name="evaluation_critere-create")
        g.add("GET", "/show/{id}", EvaluationCritereController.show, name="evaluation_critere-show")
        g.add("GET", "/edit/{id}", EvaluationCritereController.edit, name="evaluation_critere-edit")
        g.add("POST", "/update/{id}", EvaluationCritereController.update, name="evaluation_critere-update")
        g.add("POST", "/destroy/{id}", EvaluationCritereController.destroy, name="evaluation_critere-destroy")
        g.add("POST", "/bulk-delete", EvaluationCritereController.bulk_delete, name="evaluation_critere-bulk_delete")
        g.add("POST", "/bulk-delete-confirm", EvaluationCritereController.bulk_delete_confirm, name="evaluation_critere-bulk_delete_confirm")
        g.add("GET", "/export-csv", EvaluationCritereController.export_csv, name="evaluation_critere-export_csv")
