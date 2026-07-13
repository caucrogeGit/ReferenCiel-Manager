from core.forms import Form, RelationField, StringField


class ItemChecklistForm(Form):
    libelle = StringField(label="Libelle", required=True)
    section_id = RelationField(label="Section", target="SectionChecklist", required=True, choices_key="section_id_choices")
