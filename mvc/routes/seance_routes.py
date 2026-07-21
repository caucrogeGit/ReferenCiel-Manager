"""Routes du contrôleur SeanceController (ADR-068)."""
from core.http.router import Router
from mvc.controllers.seance_controller import SeanceController
from mvc.controllers.seance_editeur_controller import SeanceEditeurController


def register_seance_routes(router: Router) -> None:
    # Routes protégées par défaut. Pour un test local sans authentification :
    #   with router.group("/seance", public=True, csrf=False) as g:
    with router.group("/seance") as g:
        g.add("GET", "", SeanceController.index, name="seance-index")
        g.add("GET", "/new", SeanceController.new, name="seance-new")
        g.add("POST", "/create", SeanceController.create, name="seance-create")
        g.add("GET", "/show/{id}", SeanceController.show, name="seance-show")
        g.add("GET", "/editeur/{id}", SeanceEditeurController.editeur, name="seance-editeur")
        g.add("POST", "/{id}/fiche", SeanceEditeurController.enregistrer_fiche, name="seance-fiche")
        g.add("GET", "/edit/{id}", SeanceController.edit, name="seance-edit")
        g.add("POST", "/update/{id}", SeanceController.update, name="seance-update")
        g.add("POST", "/destroy/{id}", SeanceController.destroy, name="seance-destroy")
        g.add("POST", "/bulk-delete", SeanceController.bulk_delete, name="seance-bulk_delete")
        g.add("POST", "/bulk-delete-confirm", SeanceController.bulk_delete_confirm, name="seance-bulk_delete_confirm")
        g.add("GET", "/export-csv", SeanceController.export_csv, name="seance-export_csv")
