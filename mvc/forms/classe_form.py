from core.forms import Form, DateTimeField, RelationField, StringField


class ClasseForm(Form):
    code = StringField(label="Code", required=True)
    libelle = StringField(label="Libelle", required=False)
    created_at = DateTimeField(label="Created at", required=True)
    updated_at = DateTimeField(label="Updated at", required=True)
    annee_scolaire_id = RelationField(label="Annee scolaire", target="AnneeScolaire", required=True, choices_key="annee_scolaire_id_choices")
    niveau_classe_id = RelationField(label="Niveau classe", target="NiveauClasse", required=True, choices_key="niveau_classe_id_choices")
