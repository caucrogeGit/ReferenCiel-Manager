# pyright: strict
"""Routes du contrôleur VersionStarterController (ADR-068)."""
from core.http.router import Router
from mvc.controllers.version_starter_controller import VersionStarterController


def register_version_starter_routes(router: Router) -> None:
    # Routes protégées par défaut. Pour un test local sans authentification :
    #   with router.group("/version_starter", public=True, csrf=False) as g:
    with router.group("/version_starter") as g:
        g.add("GET", "", VersionStarterController.index, name="version_starter-index")
        g.add("GET", "/new", VersionStarterController.new, name="version_starter-new")
        g.add("POST", "/create", VersionStarterController.create, name="version_starter-create")
        g.add("GET", "/show/{id}", VersionStarterController.show, name="version_starter-show")
        g.add("GET", "/edit/{id}", VersionStarterController.edit, name="version_starter-edit")
        g.add("POST", "/update/{id}", VersionStarterController.update, name="version_starter-update")
        g.add("POST", "/destroy/{id}", VersionStarterController.destroy, name="version_starter-destroy")
        g.add("POST", "/bulk-delete", VersionStarterController.bulk_delete, name="version_starter-bulk_delete")
        g.add("POST", "/bulk-delete-confirm", VersionStarterController.bulk_delete_confirm, name="version_starter-bulk_delete_confirm")
        g.add("GET", "/export-csv", VersionStarterController.export_csv, name="version_starter-export_csv")
