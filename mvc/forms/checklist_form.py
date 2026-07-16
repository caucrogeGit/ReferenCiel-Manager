from core.forms import Form, RelationField, StringField


class ChecklistForm(Form):
    decision_finale = StringField(label="Decision finale", required=False)
    seance_id = RelationField(label="Séance", target="Seance", required=True, choices_key="seance_id_choices")
