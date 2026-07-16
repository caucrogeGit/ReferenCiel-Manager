from core.forms import Form, DateTimeField, RelationField, StringField


class EvaluationActiviteForm(Form):
    date_evaluation = DateTimeField(label="Date evaluation", required=True)
    appreciation = StringField(label="Appreciation", required=False)
    progression_seance_id = RelationField(label="Progression séance", target="ProgressionSeance", required=True, choices_key="progression_seance_id_choices")
    activite_id = RelationField(label="Activite", target="Activite", required=True, choices_key="activite_id_choices")
    professeur_id = RelationField(label="Professeur", target="Professeur", required=True, choices_key="professeur_id_choices")
