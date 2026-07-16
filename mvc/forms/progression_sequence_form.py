from core.forms import Form, DateField, RelationField, StringField


class ProgressionSequenceForm(Form):
    statut = StringField(label="Statut", required=True)
    date_debut = DateField(label="Date debut", required=False)
    eleve_id = RelationField(label="Eleve", target="Eleve", required=True, choices_key="eleve_id_choices")
    sequence_id = RelationField(label="Séquence", target="Sequence", required=True, choices_key="sequence_id_choices")
