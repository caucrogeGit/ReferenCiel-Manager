from core.forms import Form, DateField, DateTimeField, RelationField


class InscriptionEleveForm(Form):
    date_inscription = DateField(label="Date inscription", required=False)
    eleve_id = RelationField(label="Eleve", target="Eleve", required=True, choices_key="eleve_id_choices")
    classe_id = RelationField(label="Classe", target="Classe", required=True, choices_key="classe_id_choices")
    annee_scolaire_id = RelationField(label="Annee scolaire", target="AnneeScolaire", required=True, choices_key="annee_scolaire_id_choices")
    created_at = DateTimeField(label="Created at", required=True)
    updated_at = DateTimeField(label="Updated at", required=True)
