from core.forms import Form, BooleanField, DateTimeField, RelationField


class ReponseQCMForm(Form):
    est_correcte = BooleanField(label="Est correcte")
    tentative_id = RelationField(label="Tentative", target="TentativeQCM", required=True, choices_key="tentative_id_choices")
    question_id = RelationField(label="Question", target="QuestionQCM", required=True, choices_key="question_id_choices")
    choix_id = RelationField(label="Choix", target="ChoixQCM", required=True, choices_key="choix_id_choices")
    created_at = DateTimeField(label="Created at", required=True)
    updated_at = DateTimeField(label="Updated at", required=True)
