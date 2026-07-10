# pyright: strict
"""Routes du contrôleur SectionChecklistController (ADR-068)."""
from core.http.router import Router
from mvc.controllers.section_checklist_controller import SectionChecklistController


def register_section_checklist_routes(router: Router) -> None:
    # Routes protégées par défaut. Pour un test local sans authentification :
    #   with router.group("/section_checklist", public=True, csrf=False) as g:
    with router.group("/section_checklist") as g:
        g.add("GET", "", SectionChecklistController.index, name="section_checklist-index")
        g.add("GET", "/new", SectionChecklistController.new, name="section_checklist-new")
        g.add("POST", "/create", SectionChecklistController.create, name="section_checklist-create")
        g.add("GET", "/show/{id}", SectionChecklistController.show, name="section_checklist-show")
        g.add("GET", "/edit/{id}", SectionChecklistController.edit, name="section_checklist-edit")
        g.add("POST", "/update/{id}", SectionChecklistController.update, name="section_checklist-update")
        g.add("POST", "/destroy/{id}", SectionChecklistController.destroy, name="section_checklist-destroy")
        g.add("POST", "/bulk-delete", SectionChecklistController.bulk_delete, name="section_checklist-bulk_delete")
        g.add("POST", "/bulk-delete-confirm", SectionChecklistController.bulk_delete_confirm, name="section_checklist-bulk_delete_confirm")
        g.add("GET", "/export-csv", SectionChecklistController.export_csv, name="section_checklist-export_csv")
