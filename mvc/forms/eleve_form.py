from core.forms import Form, DateField, IntegerField, RelationField, StringField


class EleveForm(Form):
    nom = StringField(label="Nom", required=True)
    prenom = StringField(label="Prenom", required=True)
    identifiant = StringField(label="Identifiant", required=False)
    date_naissance = DateField(label="Date naissance", required=False)
    user_id = IntegerField(label="User id", required=False)
    niveau_classe_id = RelationField(label="Niveau de classe", target="NiveauClasse", required=True, choices_key="niveau_classe_id_choices")
