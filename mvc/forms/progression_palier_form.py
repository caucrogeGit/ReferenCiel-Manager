from core.forms import Form, RelationField, StringField


class ProgressionPalierForm(Form):
    statut = StringField(label="Statut", required=True)
    progression_parcours_id = RelationField(label="Progression eleve", target="ProgressionParcours", required=True, choices_key="progression_parcours_id_choices")
    palier_id = RelationField(label="Palier", target="Palier", required=True, choices_key="palier_id_choices")
