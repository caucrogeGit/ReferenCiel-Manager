from core.forms import Form, RelationField, StringField


class ProgressionPalierForm(Form):
    statut = StringField(label="Statut", required=True)
    progression_parcours_id = RelationField(label="Progression eleve", target="ProgressionParcours", required=True, choices_key="progression_parcours_id_choices")
    seance_id = RelationField(label="Séance", target="Seance", required=True, choices_key="seance_id_choices")
