from core.forms import Form, DateTimeField, RelationField, StringField


class EvaluationCritereForm(Form):
    niveau = StringField(label="Niveau", required=True)
    evaluation_activite_id = RelationField(label="Evaluation activite", target="EvaluationActivite", required=True, choices_key="evaluation_activite_id_choices")
    critere_id = RelationField(label="Critere", target="CritereObservable", required=True, choices_key="critere_id_choices")
    created_at = DateTimeField(label="Created at", required=True)
    updated_at = DateTimeField(label="Updated at", required=True)
