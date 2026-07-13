"""Routes du contrôleur ActiviteProfessionnelleController (ADR-068)."""
from core.http.router import Router
from mvc.controllers.activite_professionnelle_controller import ActiviteProfessionnelleController


def register_activite_professionnelle_routes(router: Router) -> None:
    # Routes protégées par défaut. Pour un test local sans authentification :
    #   with router.group("/activite_professionnelle", public=True, csrf=False) as g:
    with router.group("/activite_professionnelle") as g:
        g.add("GET", "", ActiviteProfessionnelleController.index, name="activite_professionnelle-index")
        g.add("GET", "/new", ActiviteProfessionnelleController.new, name="activite_professionnelle-new")
        g.add("POST", "/create", ActiviteProfessionnelleController.create, name="activite_professionnelle-create")
        g.add("GET", "/show/{id}", ActiviteProfessionnelleController.show, name="activite_professionnelle-show")
        g.add("GET", "/edit/{id}", ActiviteProfessionnelleController.edit, name="activite_professionnelle-edit")
        g.add("POST", "/update/{id}", ActiviteProfessionnelleController.update, name="activite_professionnelle-update")
        g.add("POST", "/destroy/{id}", ActiviteProfessionnelleController.destroy, name="activite_professionnelle-destroy")
        g.add("POST", "/bulk-delete", ActiviteProfessionnelleController.bulk_delete, name="activite_professionnelle-bulk_delete")
        g.add("POST", "/bulk-delete-confirm", ActiviteProfessionnelleController.bulk_delete_confirm, name="activite_professionnelle-bulk_delete_confirm")
        g.add("GET", "/export-csv", ActiviteProfessionnelleController.export_csv, name="activite_professionnelle-export_csv")
