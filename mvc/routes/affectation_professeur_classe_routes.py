# pyright: strict
"""Routes du contrôleur AffectationProfesseurClasseController (ADR-068)."""
from core.http.router import Router
from mvc.controllers.affectation_professeur_classe_controller import AffectationProfesseurClasseController


def register_affectation_professeur_classe_routes(router: Router) -> None:
    # Routes protégées par défaut. Pour un test local sans authentification :
    #   with router.group("/affectation_professeur_classe", public=True, csrf=False) as g:
    with router.group("/affectation_professeur_classe") as g:
        g.add("GET", "", AffectationProfesseurClasseController.index, name="affectation_professeur_classe-index")
        g.add("GET", "/new", AffectationProfesseurClasseController.new, name="affectation_professeur_classe-new")
        g.add("POST", "/create", AffectationProfesseurClasseController.create, name="affectation_professeur_classe-create")
        g.add("GET", "/show/{id}", AffectationProfesseurClasseController.show, name="affectation_professeur_classe-show")
        g.add("GET", "/edit/{id}", AffectationProfesseurClasseController.edit, name="affectation_professeur_classe-edit")
        g.add("POST", "/update/{id}", AffectationProfesseurClasseController.update, name="affectation_professeur_classe-update")
        g.add("POST", "/destroy/{id}", AffectationProfesseurClasseController.destroy, name="affectation_professeur_classe-destroy")
        g.add("POST", "/bulk-delete", AffectationProfesseurClasseController.bulk_delete, name="affectation_professeur_classe-bulk_delete")
        g.add("POST", "/bulk-delete-confirm", AffectationProfesseurClasseController.bulk_delete_confirm, name="affectation_professeur_classe-bulk_delete_confirm")
        g.add("GET", "/export-csv", AffectationProfesseurClasseController.export_csv, name="affectation_professeur_classe-export_csv")
