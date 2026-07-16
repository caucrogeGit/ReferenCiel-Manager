from core.forms import Form, RelationField, StringField


class ActiviteForm(Form):
    objectif = StringField(label="Objectif", required=False)
    fichier = StringField(label="Fichier", required=False)
    seance_id = RelationField(label="Palier", target="Palier", required=True, choices_key="palier_id_choices")
