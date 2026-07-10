from core.forms import Form, DateTimeField, RelationField, StringField


class VersionParcoursForm(Form):
    version = StringField(label="Version", required=True)
    statut = StringField(label="Statut", required=True)
    parcours_id = RelationField(label="Parcours", target="Parcours", required=True, choices_key="parcours_id_choices")
    created_at = DateTimeField(label="Created at", required=True)
    updated_at = DateTimeField(label="Updated at", required=True)
