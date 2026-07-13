from core.forms import Form, RelationField, StringField


class ChoixQCMForm(Form):
    lettre = StringField(label="Lettre", required=True)
    texte = StringField(label="Texte", required=True)
    question_id = RelationField(label="Question", target="QuestionQCM", required=True, choices_key="question_id_choices")
