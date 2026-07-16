from core.forms import Form, BooleanField, DateTimeField, IntegerField, RelationField


class TentativeQCMForm(Form):
    numero_tentative = IntegerField(label="Numero tentative", required=True)
    score = IntegerField(label="Score", required=True)
    validee = BooleanField(label="Validee")
    date_tentative = DateTimeField(label="Date tentative", required=True)
    progression_seance_id = RelationField(label="Progression séance", target="ProgressionSeance", required=True, choices_key="progression_seance_id_choices")
