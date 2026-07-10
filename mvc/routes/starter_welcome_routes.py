# pyright: strict
"""Routes du contrôleur StarterWelcomeController (ADR-068)."""
from core.http.router import Router
from mvc.controllers.starter_welcome_controller import StarterWelcomeController


def register_starter_welcome_routes(router: Router) -> None:
    # Routes protégées par défaut. Pour un test local sans authentification :
    #   with router.group("/starter_welcome", public=True, csrf=False) as g:
    with router.group("/starter_welcome") as g:
        g.add("GET", "", StarterWelcomeController.index, name="starter_welcome-index")
        g.add("GET", "/new", StarterWelcomeController.new, name="starter_welcome-new")
        g.add("POST", "/create", StarterWelcomeController.create, name="starter_welcome-create")
        g.add("GET", "/show/{id}", StarterWelcomeController.show, name="starter_welcome-show")
        g.add("GET", "/edit/{id}", StarterWelcomeController.edit, name="starter_welcome-edit")
        g.add("POST", "/update/{id}", StarterWelcomeController.update, name="starter_welcome-update")
        g.add("POST", "/destroy/{id}", StarterWelcomeController.destroy, name="starter_welcome-destroy")
        g.add("POST", "/bulk-delete", StarterWelcomeController.bulk_delete, name="starter_welcome-bulk_delete")
        g.add("POST", "/bulk-delete-confirm", StarterWelcomeController.bulk_delete_confirm, name="starter_welcome-bulk_delete_confirm")
        g.add("GET", "/export-csv", StarterWelcomeController.export_csv, name="starter_welcome-export_csv")
