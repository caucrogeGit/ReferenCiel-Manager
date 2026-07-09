from core.forms import Form, DateField, DateTimeField, IntegerField, StringField


class EleveForm(Form):
    nom = StringField(label="Nom", required=True)
    prenom = StringField(label="Prenom", required=True)
    identifiant = StringField(label="Identifiant", required=False)
    date_naissance = DateField(label="Date naissance", required=False)
    user_id = IntegerField(label="User id", required=False)
    created_at = DateTimeField(label="Created at", required=True)
    updated_at = DateTimeField(label="Updated at", required=True)
