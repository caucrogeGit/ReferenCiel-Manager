# pyright: strict
"""Routes du contrôleur AnneeScolaireController (ADR-068)."""
from core.http.router import Router
from mvc.controllers.annee_scolaire_controller import AnneeScolaireController


def register_annee_scolaire_routes(router: Router) -> None:
    # Routes protégées par défaut. Pour un test local sans authentification :
    #   with router.group("/annee_scolaire", public=True, csrf=False) as g:
    with router.group("/annee_scolaire") as g:
        g.add("GET", "", AnneeScolaireController.index, name="annee_scolaire-index")
        g.add("GET", "/new", AnneeScolaireController.new, name="annee_scolaire-new")
        g.add("POST", "/create", AnneeScolaireController.create, name="annee_scolaire-create")
        g.add("GET", "/show/{id}", AnneeScolaireController.show, name="annee_scolaire-show")
        g.add("GET", "/edit/{id}", AnneeScolaireController.edit, name="annee_scolaire-edit")
        g.add("POST", "/update/{id}", AnneeScolaireController.update, name="annee_scolaire-update")
        g.add("POST", "/destroy/{id}", AnneeScolaireController.destroy, name="annee_scolaire-destroy")
        g.add("POST", "/bulk-delete", AnneeScolaireController.bulk_delete, name="annee_scolaire-bulk_delete")
        g.add("POST", "/bulk-delete-confirm", AnneeScolaireController.bulk_delete_confirm, name="annee_scolaire-bulk_delete_confirm")
        g.add("GET", "/export-csv", AnneeScolaireController.export_csv, name="annee_scolaire-export_csv")
