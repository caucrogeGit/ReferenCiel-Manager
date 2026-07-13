"""Routes du contrôleur CompetenceController (ADR-068)."""
from core.http.router import Router
from mvc.controllers.competence_controller import CompetenceController


def register_competence_routes(router: Router) -> None:
    # Routes protégées par défaut. Pour un test local sans authentification :
    #   with router.group("/competence", public=True, csrf=False) as g:
    with router.group("/competence") as g:
        g.add("GET", "", CompetenceController.index, name="competence-index")
        g.add("GET", "/new", CompetenceController.new, name="competence-new")
        g.add("POST", "/create", CompetenceController.create, name="competence-create")
        g.add("GET", "/show/{id}", CompetenceController.show, name="competence-show")
        g.add("GET", "/edit/{id}", CompetenceController.edit, name="competence-edit")
        g.add("POST", "/update/{id}", CompetenceController.update, name="competence-update")
        g.add("POST", "/destroy/{id}", CompetenceController.destroy, name="competence-destroy")
        g.add("POST", "/bulk-delete", CompetenceController.bulk_delete, name="competence-bulk_delete")
        g.add("POST", "/bulk-delete-confirm", CompetenceController.bulk_delete_confirm, name="competence-bulk_delete_confirm")
        g.add("GET", "/export-csv", CompetenceController.export_csv, name="competence-export_csv")
