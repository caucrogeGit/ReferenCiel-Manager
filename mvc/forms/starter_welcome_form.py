from core.forms import Form, DateTimeField, RelationField, StringField


class StarterWelcomeForm(Form):
    identifiant = StringField(label="Identifiant", required=True)
    titre = StringField(label="Titre", required=True)
    presentation = StringField(label="Presentation", required=False)
    niveau_classe_id = RelationField(label="Niveau classe", target="NiveauClasse", required=True, choices_key="niveau_classe_id_choices")
    created_at = DateTimeField(label="Created at", required=True)
    updated_at = DateTimeField(label="Updated at", required=True)
