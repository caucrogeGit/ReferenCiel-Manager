from core.forms import Form, BooleanField, DateField, DateTimeField, StringField


class AnneeScolaireForm(Form):
    libelle = StringField(label="Libelle", required=True)
    date_debut = DateField(label="Date debut", required=False)
    date_fin = DateField(label="Date fin", required=False)
    active = BooleanField(label="Active")
    created_at = DateTimeField(label="Created at", required=True)
    updated_at = DateTimeField(label="Updated at", required=True)
