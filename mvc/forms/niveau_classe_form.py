from core.forms import Form, StringField


class NiveauClasseForm(Form):
    code = StringField(label="Code", required=True)
    intitule = StringField(label="Intitule", required=True)
