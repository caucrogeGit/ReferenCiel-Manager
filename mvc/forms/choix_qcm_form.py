from core.forms import Form, DateTimeField, RelationField, StringField


class ChoixQCMForm(Form):
    lettre = StringField(label="Lettre", required=True)
    texte = StringField(label="Texte", required=True)
    question_id = RelationField(label="Question", target="QuestionQCM", required=True, choices_key="question_id_choices")
    created_at = DateTimeField(label="Created at", required=True)
    updated_at = DateTimeField(label="Updated at", required=True)
