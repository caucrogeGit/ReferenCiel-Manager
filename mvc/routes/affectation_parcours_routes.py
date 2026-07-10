# pyright: strict
"""Routes du contrôleur AffectationParcoursController (ADR-068)."""
from core.http.router import Router
from mvc.controllers.affectation_parcours_controller import AffectationParcoursController


def register_affectation_parcours_routes(router: Router) -> None:
    # Routes protégées par défaut. Pour un test local sans authentification :
    #   with router.group("/affectation_parcours", public=True, csrf=False) as g:
    with router.group("/affectation_parcours") as g:
        g.add("GET", "", AffectationParcoursController.index, name="affectation_parcours-index")
        g.add("GET", "/new", AffectationParcoursController.new, name="affectation_parcours-new")
        g.add("POST", "/create", AffectationParcoursController.create, name="affectation_parcours-create")
        g.add("GET", "/show/{id}", AffectationParcoursController.show, name="affectation_parcours-show")
        g.add("GET", "/edit/{id}", AffectationParcoursController.edit, name="affectation_parcours-edit")
        g.add("POST", "/update/{id}", AffectationParcoursController.update, name="affectation_parcours-update")
        g.add("POST", "/destroy/{id}", AffectationParcoursController.destroy, name="affectation_parcours-destroy")
        g.add("POST", "/bulk-delete", AffectationParcoursController.bulk_delete, name="affectation_parcours-bulk_delete")
        g.add("POST", "/bulk-delete-confirm", AffectationParcoursController.bulk_delete_confirm, name="affectation_parcours-bulk_delete_confirm")
        g.add("GET", "/export-csv", AffectationParcoursController.export_csv, name="affectation_parcours-export_csv")
