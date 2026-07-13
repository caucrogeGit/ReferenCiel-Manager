from core.forms import Form, RelationField, StringField


class CritereObservableForm(Form):
    code = StringField(label="Code", required=True)
    libelle = StringField(label="Libelle", required=True)
    competence_id = RelationField(label="Competence", target="Competence", required=True, choices_key="competence_id_choices")
