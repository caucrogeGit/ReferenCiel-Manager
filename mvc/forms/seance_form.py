from core.forms import Form, IntegerField, RelationField, StringField


class SeanceForm(Form):
    ordre = IntegerField(label="Ordre", required=True)
    titre = StringField(label="Titre", required=True)
    theme = StringField(label="Theme", required=False)
    production_attendue = StringField(label="Production attendue", required=False)
    sequence_id = RelationField(label="Séquence", target="Sequence", required=True, choices_key="sequence_id_choices")
