from core.forms import Form, RelationField, StringField


class ParcoursForm(Form):
    titre = StringField(label="Titre", required=True)
    version_starter_id = RelationField(label="Version starter", target="VersionStarter", required=True, choices_key="version_starter_id_choices")
