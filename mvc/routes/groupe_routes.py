# pyright: strict
"""Routes du contrôleur GroupeController (ADR-068)."""
from core.http.router import Router
from mvc.controllers.groupe_controller import GroupeController


def register_groupe_routes(router: Router) -> None:
    # Routes protégées par défaut. Pour un test local sans authentification :
    #   with router.group("/groupe", public=True, csrf=False) as g:
    with router.group("/groupe") as g:
        g.add("GET", "", GroupeController.index, name="groupe-index")
        g.add("GET", "/new", GroupeController.new, name="groupe-new")
        g.add("POST", "/create", GroupeController.create, name="groupe-create")
        g.add("GET", "/show/{id}", GroupeController.show, name="groupe-show")
        g.add("GET", "/edit/{id}", GroupeController.edit, name="groupe-edit")
        g.add("POST", "/update/{id}", GroupeController.update, name="groupe-update")
        g.add("POST", "/destroy/{id}", GroupeController.destroy, name="groupe-destroy")
        g.add("POST", "/bulk-delete", GroupeController.bulk_delete, name="groupe-bulk_delete")
        g.add("POST", "/bulk-delete-confirm", GroupeController.bulk_delete_confirm, name="groupe-bulk_delete_confirm")
        g.add("GET", "/export-csv", GroupeController.export_csv, name="groupe-export_csv")
