from core.forms import Form, IntegerField, StringField


class ProfesseurForm(Form):
    nom = StringField(label="Nom", required=True)
    prenom = StringField(label="Prenom", required=True)
    user_id = IntegerField(label="User id", required=False)
