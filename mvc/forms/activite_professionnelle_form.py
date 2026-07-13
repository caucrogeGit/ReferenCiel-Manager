from core.forms import Form, RelationField, StringField


class ActiviteProfessionnelleForm(Form):
    code = StringField(label="Code", required=True)
    intitule = StringField(label="Intitule", required=True)
    conditions_exercice = StringField(label="Conditions exercice", required=False)
    referentiel_id = RelationField(label="Referentiel", target="ReferentielNiveauClasse", required=True, choices_key="referentiel_id_choices")
    pole_id = RelationField(label="Pole", target="PoleActivite", required=True, choices_key="pole_id_choices")
