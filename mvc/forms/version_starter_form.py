from core.forms import Form, BooleanField, DateTimeField, RelationField, StringField


class VersionStarterForm(Form):
    version = StringField(label="Version", required=True)
    statut = StringField(label="Statut", required=True)
    activite_glissante = BooleanField(label="Activite glissante")
    ordre_impose = BooleanField(label="Ordre impose")
    starter_id = RelationField(label="Starter", target="StarterWelcome", required=True, choices_key="starter_id_choices")
    created_at = DateTimeField(label="Created at", required=True)
    updated_at = DateTimeField(label="Updated at", required=True)
