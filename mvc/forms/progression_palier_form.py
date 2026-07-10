from core.forms import Form, DateTimeField, RelationField, StringField


class ProgressionPalierForm(Form):
    statut = StringField(label="Statut", required=True)
    progression_eleve_id = RelationField(label="Progression eleve", target="ProgressionEleve", required=True, choices_key="progression_eleve_id_choices")
    palier_id = RelationField(label="Palier", target="Palier", required=True, choices_key="palier_id_choices")
    created_at = DateTimeField(label="Created at", required=True)
    updated_at = DateTimeField(label="Updated at", required=True)
