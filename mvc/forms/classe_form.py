from core.forms import Form, RelationField, StringField


class ClasseForm(Form):
    code = StringField(label="Code", required=True)
    libelle = StringField(label="Libelle", required=False)
    annee_scolaire_id = RelationField(label="Annee scolaire", target="AnneeScolaire", required=True, choices_key="annee_scolaire_id_choices")
    formation_niveau_id = RelationField(label="Formation-niveau", target="FormationNiveau", required=True, choices_key="formation_niveau_id_choices")
