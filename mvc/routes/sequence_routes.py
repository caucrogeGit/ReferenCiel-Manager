"""Routes du contrôleur SequenceController (ADR-068)."""
from core.http.router import Router
from mvc.controllers.sequence_controller import SequenceController
from mvc.controllers.sequence_connaissance_controller import SequenceConnaissanceController
from mvc.controllers.sequence_editeur_controller import SequenceEditeurController


def register_sequence_routes(router: Router) -> None:
    # Routes protégées par défaut. Pour un test local sans authentification :
    #   with router.group("/sequence", public=True, csrf=False) as g:
    with router.group("/sequence") as g:
        g.add("GET", "", SequenceController.index, name="sequence-index")
        g.add("GET", "/new", SequenceController.new, name="sequence-new")
        g.add("POST", "/create", SequenceController.create, name="sequence-create")
        g.add("POST", "/nouveau", SequenceEditeurController.nouveau, name="sequence-nouveau")
        g.add("GET", "/show/{id}", SequenceController.show, name="sequence-show")
        g.add("GET", "/editeur/{id}", SequenceEditeurController.editeur, name="sequence-editeur")
        g.add("POST", "/{id}/identite", SequenceEditeurController.enregistrer_identite, name="sequence-identite")
        g.add("POST", "/{id}/cadre", SequenceEditeurController.enregistrer_cadre, name="sequence-cadre")
        g.add("GET", "/edit/{id}", SequenceController.edit, name="sequence-edit")
        g.add("POST", "/update/{id}", SequenceController.update, name="sequence-update")
        g.add("GET", "/{id}/connaissances", SequenceConnaissanceController.afficher, name="sequence-connaissances")
        g.add("POST", "/{id}/referentiel", SequenceConnaissanceController.rattacher_referentiel, name="sequence-referentiel")
        g.add("POST", "/{id}/savoir-libre/ajouter", SequenceConnaissanceController.ajouter_savoir, name="sequence-savoir-libre-ajouter")
        g.add("POST", "/savoir-libre/{sid}/supprimer", SequenceConnaissanceController.supprimer_savoir, name="sequence-savoir-libre-supprimer")
        g.add("POST", "/{id}/connaissance/basculer", SequenceConnaissanceController.basculer, name="sequence-connaissance-basculer")
        g.add("POST", "/{id}/connaissance/niveau", SequenceConnaissanceController.niveau, name="sequence-connaissance-niveau")
        g.add("POST", "/{id}/connaissance/statut", SequenceConnaissanceController.statut, name="sequence-connaissance-statut")
        g.add("POST", "/destroy/{id}", SequenceController.destroy, name="sequence-destroy")
        g.add("POST", "/bulk-delete", SequenceController.bulk_delete, name="sequence-bulk_delete")
        g.add("POST", "/bulk-delete-confirm", SequenceController.bulk_delete_confirm, name="sequence-bulk_delete_confirm")
        g.add("GET", "/export-csv", SequenceController.export_csv, name="sequence-export_csv")
        g.add("GET", "/{id}/pdf", SequenceController.telecharger_pdf, name="sequence-pdf")
        g.add("GET", "/{id}/md", SequenceController.telecharger_md, name="sequence-md")
        g.add("GET", "/{id}/json", SequenceController.telecharger_json, name="sequence-json")
