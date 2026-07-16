from core.forms import Form, RelationField, StringField


class ProgressionSeanceForm(Form):
    statut = StringField(label="Statut", required=True)
    progression_sequence_id = RelationField(label="Progression de séquence", target="ProgressionSequence", required=True, choices_key="progression_sequence_id_choices")
    seance_id = RelationField(label="Séance", target="Seance", required=True, choices_key="seance_id_choices")
