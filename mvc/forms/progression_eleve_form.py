from core.forms import Form, DateField, RelationField, StringField


class ProgressionEleveForm(Form):
    statut = StringField(label="Statut", required=True)
    date_debut = DateField(label="Date debut", required=False)
    eleve_id = RelationField(label="Eleve", target="Eleve", required=True, choices_key="eleve_id_choices")
    affectation_parcours_id = RelationField(label="Affectation parcours", target="AffectationParcours", required=True, choices_key="affectation_parcours_id_choices")
