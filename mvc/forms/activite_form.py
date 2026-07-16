from core.forms import Form, RelationField, StringField


class ActiviteForm(Form):
    objectif = StringField(label="Objectif", required=False)
    fichier = StringField(label="Fichier", required=False)
    seance_id = RelationField(label="Séance", target="Seance", required=True, choices_key="seance_id_choices")
