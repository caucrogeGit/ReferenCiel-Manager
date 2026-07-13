from core.forms import Form, RelationField, StringField


class ScenarioForm(Form):
    titre = StringField(label="Titre", required=True)
    intention = StringField(label="Intention", required=True)
    objectifs = StringField(label="Objectifs", required=False)
    statut = StringField(label="Statut", required=True)
    version = StringField(label="Version", required=True)
    referentiel_id = RelationField(label="Referentiel", target="ReferentielNiveauClasse", required=True, choices_key="referentiel_id_choices")
    auteur_id = RelationField(label="Auteur", target="Professeur", required=True, choices_key="auteur_id_choices")
