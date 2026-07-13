from core.forms import Form, RelationField, StringField


class QCMForm(Form):
    format_reponse = StringField(label="Format reponse", required=False)
    seuil_validation = StringField(label="Seuil validation", required=True)
    palier_id = RelationField(label="Palier", target="Palier", required=True, choices_key="palier_id_choices")
