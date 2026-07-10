from core.forms import Form, DateTimeField, IntegerField, RelationField, StringField


class SectionChecklistForm(Form):
    numero = IntegerField(label="Numero", required=True)
    titre = StringField(label="Titre", required=True)
    checklist_id = RelationField(label="Checklist", target="Checklist", required=True, choices_key="checklist_id_choices")
    created_at = DateTimeField(label="Created at", required=True)
    updated_at = DateTimeField(label="Updated at", required=True)
