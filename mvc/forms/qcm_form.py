from core.forms import Form, RelationField, StringField


class QCMForm(Form):
    format_reponse = StringField(label="Format reponse", required=False)
    seuil_validation = StringField(label="Seuil validation", required=True)
    dossier_technique_id = RelationField(label="Dossier technique", target="DossierTechnique", required=True, choices_key="dossier_technique_id_choices")
