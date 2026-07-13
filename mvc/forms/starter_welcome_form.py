from core.forms import Form, RelationField, StringField


class StarterWelcomeForm(Form):
    identifiant = StringField(label="Identifiant", required=True)
    titre = StringField(label="Titre", required=True)
    presentation = StringField(label="Presentation", required=False)
    niveau_classe_id = RelationField(label="Niveau classe", target="NiveauClasse", required=True, choices_key="niveau_classe_id_choices")
