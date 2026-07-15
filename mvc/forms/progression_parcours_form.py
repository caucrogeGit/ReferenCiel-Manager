from core.forms import Form, DateField, RelationField, StringField


class ProgressionParcoursForm(Form):
    statut = StringField(label="Statut", required=True)
    date_debut = DateField(label="Date debut", required=False)
    eleve_id = RelationField(label="Eleve", target="Eleve", required=True, choices_key="eleve_id_choices")
    parcours_id = RelationField(label="Parcours", target="Parcours", required=True, choices_key="parcours_id_choices")
