from core.forms import Form, DateTimeField, RelationField, StringField


class ItemChecklistForm(Form):
    libelle = StringField(label="Libelle", required=True)
    section_id = RelationField(label="Section", target="SectionChecklist", required=True, choices_key="section_id_choices")
    created_at = DateTimeField(label="Created at", required=True)
    updated_at = DateTimeField(label="Updated at", required=True)
