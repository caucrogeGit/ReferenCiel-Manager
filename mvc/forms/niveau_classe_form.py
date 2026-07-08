from core.forms import Form, DateTimeField, StringField


class NiveauClasseForm(Form):
    code = StringField(label="Code", required=True)
    intitule = StringField(label="Intitule", required=True)
    created_at = DateTimeField(label="Created at", required=True)
    updated_at = DateTimeField(label="Updated at", required=True)
