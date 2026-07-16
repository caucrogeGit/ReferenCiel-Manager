"""Routes du contrôleur ProgressionSequenceController (ADR-068)."""
from core.http.router import Router
from mvc.controllers.progression_sequence_controller import ProgressionSequenceController


def register_progression_sequence_routes(router: Router) -> None:
    # Routes protégées par défaut. Pour un test local sans authentification :
    #   with router.group("/progression_sequence", public=True, csrf=False) as g:
    with router.group("/progression_sequence") as g:
        g.add("GET", "", ProgressionSequenceController.index, name="progression_sequence-index")
        g.add("GET", "/new", ProgressionSequenceController.new, name="progression_sequence-new")
        g.add("POST", "/create", ProgressionSequenceController.create, name="progression_sequence-create")
        g.add("GET", "/show/{id}", ProgressionSequenceController.show, name="progression_sequence-show")
        g.add("GET", "/edit/{id}", ProgressionSequenceController.edit, name="progression_sequence-edit")
        g.add("POST", "/update/{id}", ProgressionSequenceController.update, name="progression_sequence-update")
        g.add("POST", "/destroy/{id}", ProgressionSequenceController.destroy, name="progression_sequence-destroy")
        g.add("POST", "/bulk-delete", ProgressionSequenceController.bulk_delete, name="progression_sequence-bulk_delete")
        g.add("POST", "/bulk-delete-confirm", ProgressionSequenceController.bulk_delete_confirm, name="progression_sequence-bulk_delete_confirm")
        g.add("GET", "/export-csv", ProgressionSequenceController.export_csv, name="progression_sequence-export_csv")
