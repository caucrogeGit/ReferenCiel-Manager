"""Routes du contrôleur SeanceController (ADR-068)."""
from core.http.router import Router
from mvc.controllers.seance_controller import SeanceController
from mvc.controllers.seance_connaissance_controller import SeanceConnaissanceController
from mvc.controllers.seance_editeur_controller import SeanceEditeurController


def register_seance_routes(router: Router) -> None:
    # Routes protégées par défaut. Pour un test local sans authentification :
    #   with router.group("/seance", public=True, csrf=False) as g:
    with router.group("/seance") as g:
        g.add("GET", "", SeanceController.index, name="seance-index")
        g.add("GET", "/new", SeanceController.new, name="seance-new")
        g.add("POST", "/create", SeanceController.create, name="seance-create")
        g.add("POST", "/nouveau", SeanceEditeurController.nouveau, name="seance-nouveau")
        g.add("GET", "/show/{id}", SeanceController.show, name="seance-show")
        g.add("GET", "/editeur/{id}", SeanceEditeurController.editeur, name="seance-editeur")
        g.add("POST", "/{id}/fiche", SeanceEditeurController.enregistrer_fiche, name="seance-fiche")
        g.add("GET", "/{id}/savoirs", SeanceConnaissanceController.afficher, name="seance-savoirs")
        g.add("POST", "/{id}/savoir/basculer", SeanceConnaissanceController.basculer, name="seance-savoir-basculer")
        g.add("POST", "/{id}/savoir/niveau", SeanceConnaissanceController.niveau, name="seance-savoir-niveau")
        g.add("POST", "/{id}/savoir/statut", SeanceConnaissanceController.statut, name="seance-savoir-statut")
        g.add("GET", "/{id}/competences", SeanceEditeurController.afficher_competences, name="seance-competences")
        g.add("POST", "/{id}/competence/role", SeanceEditeurController.changer_role, name="seance-competence-role")
        g.add("POST", "/{id}/critere/basculer", SeanceEditeurController.basculer_critere, name="seance-critere-basculer")
        g.add("POST", "/{id}/element/ajouter", SeanceEditeurController.ajouter_element, name="seance-element-ajouter")
        g.add("POST", "/element/{eid}/maj", SeanceEditeurController.maj_element, name="seance-element-maj")
        g.add("POST", "/element/{eid}/supprimer", SeanceEditeurController.supprimer_element, name="seance-element-supprimer")
        g.add("POST", "/element/{eid}/deplacer", SeanceEditeurController.deplacer_element, name="seance-element-deplacer")
        g.add("GET", "/edit/{id}", SeanceController.edit, name="seance-edit")
        g.add("POST", "/update/{id}", SeanceController.update, name="seance-update")
        g.add("POST", "/destroy/{id}", SeanceController.destroy, name="seance-destroy")
        g.add("POST", "/bulk-delete", SeanceController.bulk_delete, name="seance-bulk_delete")
        g.add("POST", "/bulk-delete-confirm", SeanceController.bulk_delete_confirm, name="seance-bulk_delete_confirm")
        g.add("GET", "/export-csv", SeanceController.export_csv, name="seance-export_csv")
