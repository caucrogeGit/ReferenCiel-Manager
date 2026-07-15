from core.forms import Form, DateField, IntegerField, RelationField, StringField


class EleveForm(Form):
    nom = StringField(label="Nom", required=True)
    prenom = StringField(label="Prenom", required=True)
    identifiant = StringField(label="Identifiant", required=False)
    date_naissance = DateField(label="Date naissance", required=False)
    user_id = IntegerField(label="User id", required=False)
    classe_id = RelationField(label="Classe", target="Classe", required=True, choices_key="classe_id_choices")
