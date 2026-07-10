from core.forms import Form, DateField, DateTimeField, RelationField, StringField


class AffectationParcoursForm(Form):
    date_affectation = DateField(label="Date affectation", required=True)
    statut = StringField(label="Statut", required=True)
    version_parcours_id = RelationField(label="Version parcours", target="VersionParcours", required=True, choices_key="version_parcours_id_choices")
    classe_id = RelationField(label="Classe", target="Classe", required=True, choices_key="classe_id_choices")
    professeur_id = RelationField(label="Professeur", target="Professeur", required=True, choices_key="professeur_id_choices")
    created_at = DateTimeField(label="Created at", required=True)
    updated_at = DateTimeField(label="Updated at", required=True)
