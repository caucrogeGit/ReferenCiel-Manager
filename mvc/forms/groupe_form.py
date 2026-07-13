from core.forms import Form, RelationField, StringField


class GroupeForm(Form):
    nom = StringField(label="Nom", required=True)
    classe_id = RelationField(label="Classe", target="Classe", required=True, choices_key="classe_id_choices")
