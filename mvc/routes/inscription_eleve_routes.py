# pyright: strict
"""Routes du contrôleur InscriptionEleveController (ADR-068)."""
from core.http.router import Router
from mvc.controllers.inscription_eleve_controller import InscriptionEleveController


def register_inscription_eleve_routes(router: Router) -> None:
    # Routes protégées par défaut. Pour un test local sans authentification :
    #   with router.group("/inscription_eleve", public=True, csrf=False) as g:
    with router.group("/inscription_eleve") as g:
        g.add("GET", "", InscriptionEleveController.index, name="inscription_eleve-index")
        g.add("GET", "/new", InscriptionEleveController.new, name="inscription_eleve-new")
        g.add("POST", "/create", InscriptionEleveController.create, name="inscription_eleve-create")
        g.add("GET", "/show/{id}", InscriptionEleveController.show, name="inscription_eleve-show")
        g.add("GET", "/edit/{id}", InscriptionEleveController.edit, name="inscription_eleve-edit")
        g.add("POST", "/update/{id}", InscriptionEleveController.update, name="inscription_eleve-update")
        g.add("POST", "/destroy/{id}", InscriptionEleveController.destroy, name="inscription_eleve-destroy")
        g.add("POST", "/bulk-delete", InscriptionEleveController.bulk_delete, name="inscription_eleve-bulk_delete")
        g.add("POST", "/bulk-delete-confirm", InscriptionEleveController.bulk_delete_confirm, name="inscription_eleve-bulk_delete_confirm")
        g.add("GET", "/export-csv", InscriptionEleveController.export_csv, name="inscription_eleve-export_csv")
