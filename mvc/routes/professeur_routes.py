# pyright: strict
"""Routes du contrôleur ProfesseurController (ADR-068)."""
from core.http.router import Router
from mvc.controllers.professeur_controller import ProfesseurController


def register_professeur_routes(router: Router) -> None:
    # Routes protégées par défaut. Pour un test local sans authentification :
    #   with router.group("/professeur", public=True, csrf=False) as g:
    with router.group("/professeur") as g:
        g.add("GET", "", ProfesseurController.index, name="professeur-index")
        g.add("GET", "/new", ProfesseurController.new, name="professeur-new")
        g.add("POST", "/create", ProfesseurController.create, name="professeur-create")
        g.add("GET", "/show/{id}", ProfesseurController.show, name="professeur-show")
        g.add("GET", "/edit/{id}", ProfesseurController.edit, name="professeur-edit")
        g.add("POST", "/update/{id}", ProfesseurController.update, name="professeur-update")
        g.add("POST", "/destroy/{id}", ProfesseurController.destroy, name="professeur-destroy")
        g.add("POST", "/bulk-delete", ProfesseurController.bulk_delete, name="professeur-bulk_delete")
        g.add("POST", "/bulk-delete-confirm", ProfesseurController.bulk_delete_confirm, name="professeur-bulk_delete_confirm")
        g.add("GET", "/export-csv", ProfesseurController.export_csv, name="professeur-export_csv")
