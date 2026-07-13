from core.forms import Form, RelationField, StringField


class ChecklistForm(Form):
    decision_finale = StringField(label="Decision finale", required=False)
    palier_id = RelationField(label="Palier", target="Palier", required=True, choices_key="palier_id_choices")
