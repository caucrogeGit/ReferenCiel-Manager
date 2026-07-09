from core.forms import Form, DateTimeField, IntegerField, StringField


class ProfesseurForm(Form):
    nom = StringField(label="Nom", required=True)
    prenom = StringField(label="Prenom", required=True)
    user_id = IntegerField(label="User id", required=False)
    created_at = DateTimeField(label="Created at", required=True)
    updated_at = DateTimeField(label="Updated at", required=True)
