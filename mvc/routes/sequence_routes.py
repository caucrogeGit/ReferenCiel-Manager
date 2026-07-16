"""Routes du contrôleur SequenceController (ADR-068)."""
from core.http.router import Router
from mvc.controllers.sequence_controller import SequenceController


def register_sequence_routes(router: Router) -> None:
    # Routes protégées par défaut. Pour un test local sans authentification :
    #   with router.group("/sequence", public=True, csrf=False) as g:
    with router.group("/sequence") as g:
        g.add("GET", "", SequenceController.index, name="sequence-index")
        g.add("GET", "/new", SequenceController.new, name="sequence-new")
        g.add("POST", "/create", SequenceController.create, name="sequence-create")
        g.add("GET", "/show/{id}", SequenceController.show, name="sequence-show")
        g.add("GET", "/edit/{id}", SequenceController.edit, name="sequence-edit")
        g.add("POST", "/update/{id}", SequenceController.update, name="sequence-update")
        g.add("POST", "/destroy/{id}", SequenceController.destroy, name="sequence-destroy")
        g.add("POST", "/bulk-delete", SequenceController.bulk_delete, name="sequence-bulk_delete")
        g.add("POST", "/bulk-delete-confirm", SequenceController.bulk_delete_confirm, name="sequence-bulk_delete_confirm")
        g.add("GET", "/export-csv", SequenceController.export_csv, name="sequence-export_csv")
