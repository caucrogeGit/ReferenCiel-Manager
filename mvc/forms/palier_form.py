from core.forms import Form, IntegerField, RelationField, StringField


class PalierForm(Form):
    ordre = IntegerField(label="Ordre", required=True)
    titre = StringField(label="Titre", required=True)
    theme = StringField(label="Theme", required=False)
    production_attendue = StringField(label="Production attendue", required=False)
    parcours_id = RelationField(label="Parcours", target="Parcours", required=True, choices_key="parcours_id_choices")
