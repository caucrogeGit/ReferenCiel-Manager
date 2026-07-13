from core.forms import Form, DateField, RelationField


class InscriptionEleveForm(Form):
    date_inscription = DateField(label="Date inscription", required=False)
    eleve_id = RelationField(label="Eleve", target="Eleve", required=True, choices_key="eleve_id_choices")
    classe_id = RelationField(label="Classe", target="Classe", required=True, choices_key="classe_id_choices")
    annee_scolaire_id = RelationField(label="Annee scolaire", target="AnneeScolaire", required=True, choices_key="annee_scolaire_id_choices")
