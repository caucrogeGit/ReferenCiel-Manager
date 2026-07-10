# pyright: strict
"""Routes du contrôleur EvaluationActiviteController (ADR-068)."""
from core.http.router import Router
from mvc.controllers.evaluation_activite_controller import EvaluationActiviteController


def register_evaluation_activite_routes(router: Router) -> None:
    # Routes protégées par défaut. Pour un test local sans authentification :
    #   with router.group("/evaluation_activite", public=True, csrf=False) as g:
    with router.group("/evaluation_activite") as g:
        g.add("GET", "", EvaluationActiviteController.index, name="evaluation_activite-index")
        g.add("GET", "/new", EvaluationActiviteController.new, name="evaluation_activite-new")
        g.add("POST", "/create", EvaluationActiviteController.create, name="evaluation_activite-create")
        g.add("GET", "/show/{id}", EvaluationActiviteController.show, name="evaluation_activite-show")
        g.add("GET", "/edit/{id}", EvaluationActiviteController.edit, name="evaluation_activite-edit")
        g.add("POST", "/update/{id}", EvaluationActiviteController.update, name="evaluation_activite-update")
        g.add("POST", "/destroy/{id}", EvaluationActiviteController.destroy, name="evaluation_activite-destroy")
        g.add("POST", "/bulk-delete", EvaluationActiviteController.bulk_delete, name="evaluation_activite-bulk_delete")
        g.add("POST", "/bulk-delete-confirm", EvaluationActiviteController.bulk_delete_confirm, name="evaluation_activite-bulk_delete_confirm")
        g.add("GET", "/export-csv", EvaluationActiviteController.export_csv, name="evaluation_activite-export_csv")
