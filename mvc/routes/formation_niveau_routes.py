"""Routes du contrôleur FormationNiveauController (ADR-068)."""
from core.http.router import Router
from mvc.controllers.formation_niveau_controller import FormationNiveauController


def register_formation_niveau_routes(router: Router) -> None:
    # Routes protégées par défaut. Pour un test local sans authentification :
    #   with router.group("/formation_niveau", public=True, csrf=False) as g:
    with router.group("/formation_niveau") as g:
        g.add("GET", "", FormationNiveauController.index, name="formation_niveau-index")
        g.add("GET", "/new", FormationNiveauController.new, name="formation_niveau-new")
        g.add("POST", "/create", FormationNiveauController.create, name="formation_niveau-create")
        g.add("GET", "/show/{id}", FormationNiveauController.show, name="formation_niveau-show")
        g.add("GET", "/edit/{id}", FormationNiveauController.edit, name="formation_niveau-edit")
        g.add("POST", "/update/{id}", FormationNiveauController.update, name="formation_niveau-update")
        g.add("POST", "/destroy/{id}", FormationNiveauController.destroy, name="formation_niveau-destroy")
        g.add("POST", "/bulk-delete", FormationNiveauController.bulk_delete, name="formation_niveau-bulk_delete")
        g.add("POST", "/bulk-delete-confirm", FormationNiveauController.bulk_delete_confirm, name="formation_niveau-bulk_delete_confirm")
        g.add("GET", "/export-csv", FormationNiveauController.export_csv, name="formation_niveau-export_csv")
