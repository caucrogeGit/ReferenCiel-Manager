from core.forms import Form, RelationField, StringField


class FamilleCompetenceForm(Form):
    code = StringField(label="Code", required=True)
    intitule = StringField(label="Intitule", required=True)
    referentiel_id = RelationField(label="Referentiel", target="ReferentielNiveauClasse", required=True, choices_key="referentiel_id_choices")
