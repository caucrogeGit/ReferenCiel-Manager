from core.forms import Form, DateTimeField, RelationField, StringField


class DepotEleveForm(Form):
    fichier = StringField(label="Fichier", required=True)
    commentaire = StringField(label="Commentaire", required=False)
    date_depot = DateTimeField(label="Date depot", required=True)
    progression_seance_id = RelationField(label="Progression séance", target="ProgressionSeance", required=True, choices_key="progression_seance_id_choices")
    activite_id = RelationField(label="Activite", target="Activite", required=True, choices_key="activite_id_choices")
