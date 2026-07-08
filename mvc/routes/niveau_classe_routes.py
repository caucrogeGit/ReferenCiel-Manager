# pyright: strict
"""Routes du contrôleur NiveauClasseController (ADR-068)."""
from core.http.router import Router
from mvc.controllers.niveau_classe_controller import NiveauClasseController


def register_niveau_classe_routes(router: Router) -> None:
    # Routes protégées par défaut. Pour un test local sans authentification :
    #   with router.group("/niveau_classe", public=True, csrf=False) as g:
    with router.group("/niveau_classe") as g:
        g.add("GET", "", NiveauClasseController.index, name="niveau_classe-index")
        g.add("GET", "/new", NiveauClasseController.new, name="niveau_classe-new")
        g.add("POST", "/create", NiveauClasseController.create, name="niveau_classe-create")
        g.add("GET", "/show/{id}", NiveauClasseController.show, name="niveau_classe-show")
        g.add("GET", "/edit/{id}", NiveauClasseController.edit, name="niveau_classe-edit")
        g.add("POST", "/update/{id}", NiveauClasseController.update, name="niveau_classe-update")
        g.add("POST", "/destroy/{id}", NiveauClasseController.destroy, name="niveau_classe-destroy")
        g.add("POST", "/bulk-delete", NiveauClasseController.bulk_delete, name="niveau_classe-bulk_delete")
        g.add("POST", "/bulk-delete-confirm", NiveauClasseController.bulk_delete_confirm, name="niveau_classe-bulk_delete_confirm")
        g.add("GET", "/export-csv", NiveauClasseController.export_csv, name="niveau_classe-export_csv")
