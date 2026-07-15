from core.forms import Form, BooleanField, RelationField, StringField


class ParcoursForm(Form):
    identifiant = StringField(label="Identifiant", required=True)
    titre = StringField(label="Titre", required=True)
    presentation = StringField(label="Presentation", required=False)
    statut = StringField(label="Statut", required=True)
    activite_glissante = BooleanField(label="Activite glissante")
    ordre_impose = BooleanField(label="Ordre impose")
    niveau_classe_id = RelationField(label="Niveau classe", target="NiveauClasse", required=True, choices_key="niveau_classe_id_choices")
