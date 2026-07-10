from core.forms import Form, DateTimeField, RelationField, StringField


class DepotEleveForm(Form):
    fichier = StringField(label="Fichier", required=True)
    commentaire = StringField(label="Commentaire", required=False)
    date_depot = DateTimeField(label="Date depot", required=True)
    progression_palier_id = RelationField(label="Progression palier", target="ProgressionPalier", required=True, choices_key="progression_palier_id_choices")
    activite_id = RelationField(label="Activite", target="Activite", required=True, choices_key="activite_id_choices")
    created_at = DateTimeField(label="Created at", required=True)
    updated_at = DateTimeField(label="Updated at", required=True)
