# pyright: strict
"""Routes du contrôleur VersionParcoursController (ADR-068)."""
from core.http.router import Router
from mvc.controllers.version_parcours_controller import VersionParcoursController


def register_version_parcours_routes(router: Router) -> None:
    # Routes protégées par défaut. Pour un test local sans authentification :
    #   with router.group("/version_parcours", public=True, csrf=False) as g:
    with router.group("/version_parcours") as g:
        g.add("GET", "", VersionParcoursController.index, name="version_parcours-index")
        g.add("GET", "/new", VersionParcoursController.new, name="version_parcours-new")
        g.add("POST", "/create", VersionParcoursController.create, name="version_parcours-create")
        g.add("GET", "/show/{id}", VersionParcoursController.show, name="version_parcours-show")
        g.add("GET", "/edit/{id}", VersionParcoursController.edit, name="version_parcours-edit")
        g.add("POST", "/update/{id}", VersionParcoursController.update, name="version_parcours-update")
        g.add("POST", "/destroy/{id}", VersionParcoursController.destroy, name="version_parcours-destroy")
        g.add("POST", "/bulk-delete", VersionParcoursController.bulk_delete, name="version_parcours-bulk_delete")
        g.add("POST", "/bulk-delete-confirm", VersionParcoursController.bulk_delete_confirm, name="version_parcours-bulk_delete_confirm")
        g.add("GET", "/export-csv", VersionParcoursController.export_csv, name="version_parcours-export_csv")
