from core.forms import Form, BooleanField, DateField, StringField


class AnneeScolaireForm(Form):
    libelle = StringField(label="Libelle", required=True)
    date_debut = DateField(label="Date debut", required=False)
    date_fin = DateField(label="Date fin", required=False)
    active = BooleanField(label="Active")
