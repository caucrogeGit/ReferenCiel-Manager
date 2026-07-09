from core.forms import Form, DateTimeField, RelationField, StringField


class AffectationProfesseurClasseForm(Form):
    role = StringField(label="Role", required=False)
    professeur_id = RelationField(label="Professeur", target="Professeur", required=True, choices_key="professeur_id_choices")
    classe_id = RelationField(label="Classe", target="Classe", required=True, choices_key="classe_id_choices")
    annee_scolaire_id = RelationField(label="Annee scolaire", target="AnneeScolaire", required=True, choices_key="annee_scolaire_id_choices")
    created_at = DateTimeField(label="Created at", required=True)
    updated_at = DateTimeField(label="Updated at", required=True)
