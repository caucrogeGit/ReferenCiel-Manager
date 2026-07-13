from core.forms import Form, IntegerField, RelationField, StringField


class QuestionQCMForm(Form):
    numero = IntegerField(label="Numero", required=True)
    enonce = StringField(label="Enonce", required=True)
    bonne_reponse = StringField(label="Bonne reponse", required=True)
    qcm_id = RelationField(label="Qcm", target="QCM", required=True, choices_key="qcm_id_choices")
