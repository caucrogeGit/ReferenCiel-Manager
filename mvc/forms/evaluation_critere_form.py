from core.forms import Form, RelationField, StringField


class EvaluationCritereForm(Form):
    niveau = StringField(label="Niveau", required=True)
    evaluation_activite_id = RelationField(label="Evaluation activite", target="EvaluationActivite", required=True, choices_key="evaluation_activite_id_choices")
    critere_id = RelationField(label="Critere", target="CritereObservable", required=True, choices_key="critere_id_choices")
