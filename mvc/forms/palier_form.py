from core.forms import Form, IntegerField, RelationField, StringField


class PalierForm(Form):
    ordre = IntegerField(label="Ordre", required=True)
    titre = StringField(label="Titre", required=True)
    theme = StringField(label="Theme", required=False)
    production_attendue = StringField(label="Production attendue", required=False)
    dossier_technique_fichier = StringField(label="Dossier technique fichier", required=True)
    version_parcours_id = RelationField(label="Version parcours", target="VersionParcours", required=True, choices_key="version_parcours_id_choices")
