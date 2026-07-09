from core.forms import Form, DateTimeField, RelationField, StringField


class GroupeForm(Form):
    nom = StringField(label="Nom", required=True)
    classe_id = RelationField(label="Classe", target="Classe", required=True, choices_key="classe_id_choices")
    created_at = DateTimeField(label="Created at", required=True)
    updated_at = DateTimeField(label="Updated at", required=True)
