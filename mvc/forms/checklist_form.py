from core.forms import Form, DateTimeField, RelationField, StringField


class ChecklistForm(Form):
    decision_finale = StringField(label="Decision finale", required=False)
    palier_id = RelationField(label="Palier", target="Palier", required=True, choices_key="palier_id_choices")
    created_at = DateTimeField(label="Created at", required=True)
    updated_at = DateTimeField(label="Updated at", required=True)
