from core.forms import Form, DateTimeField, RelationField, StringField


class ParcoursForm(Form):
    titre = StringField(label="Titre", required=True)
    version_starter_id = RelationField(label="Version starter", target="VersionStarter", required=True, choices_key="version_starter_id_choices")
    created_at = DateTimeField(label="Created at", required=True)
    updated_at = DateTimeField(label="Updated at", required=True)
