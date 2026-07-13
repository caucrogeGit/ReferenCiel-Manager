from core.forms import Form, IntegerField, RelationField, StringField


class SectionChecklistForm(Form):
    numero = IntegerField(label="Numero", required=True)
    titre = StringField(label="Titre", required=True)
    checklist_id = RelationField(label="Checklist", target="Checklist", required=True, choices_key="checklist_id_choices")
