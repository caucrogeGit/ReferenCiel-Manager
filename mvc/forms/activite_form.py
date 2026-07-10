from core.forms import Form, DateTimeField, RelationField, StringField


class ActiviteForm(Form):
    objectif = StringField(label="Objectif", required=False)
    fichier = StringField(label="Fichier", required=False)
    palier_id = RelationField(label="Palier", target="Palier", required=True, choices_key="palier_id_choices")
    created_at = DateTimeField(label="Created at", required=True)
    updated_at = DateTimeField(label="Updated at", required=True)
