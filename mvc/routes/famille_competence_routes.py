"""Routes du contrôleur FamilleCompetenceController (ADR-068)."""
from core.http.router import Router
from mvc.controllers.famille_competence_controller import FamilleCompetenceController


def register_famille_competence_routes(router: Router) -> None:
    # Routes protégées par défaut. Pour un test local sans authentification :
    #   with router.group("/famille_competence", public=True, csrf=False) as g:
    with router.group("/famille_competence") as g:
        g.add("GET", "", FamilleCompetenceController.index, name="famille_competence-index")
        g.add("GET", "/new", FamilleCompetenceController.new, name="famille_competence-new")
        g.add("POST", "/create", FamilleCompetenceController.create, name="famille_competence-create")
        g.add("GET", "/show/{id}", FamilleCompetenceController.show, name="famille_competence-show")
        g.add("GET", "/edit/{id}", FamilleCompetenceController.edit, name="famille_competence-edit")
        g.add("POST", "/update/{id}", FamilleCompetenceController.update, name="famille_competence-update")
        g.add("POST", "/destroy/{id}", FamilleCompetenceController.destroy, name="famille_competence-destroy")
        g.add("POST", "/bulk-delete", FamilleCompetenceController.bulk_delete, name="famille_competence-bulk_delete")
        g.add("POST", "/bulk-delete-confirm", FamilleCompetenceController.bulk_delete_confirm, name="famille_competence-bulk_delete_confirm")
        g.add("GET", "/export-csv", FamilleCompetenceController.export_csv, name="famille_competence-export_csv")
