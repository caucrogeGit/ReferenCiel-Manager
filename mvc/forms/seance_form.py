from core.forms import Form, IntegerField, RelationField, StringField, TextAreaField


class SeanceForm(Form):
    ordre = IntegerField(label="Ordre", required=True)
    titre = StringField(label="Titre", required=True)
    theme = StringField(label="Theme", required=False)
    production_attendue = StringField(label="Production attendue", required=False)
    # Champs institutionnels (SEQ-02, vademecum voie pro), tous optionnels.
    objectif_operationnel = TextAreaField(label="Objectif opérationnel", required=False)
    consigne_generale = TextAreaField(label="Consigne générale", required=False)
    duree_estimee_minutes = IntegerField(label="Durée estimée (minutes)", required=False, min_value=0)
    modalite_pedagogique = StringField(label="Modalité pédagogique", required=False)
    condition_realisation = TextAreaField(label="Conditions de réalisation", required=False)
    condition_validation = TextAreaField(label="Conditions de validation", required=False)
    remediation = TextAreaField(label="Remédiation", required=False)
    sequence_id = RelationField(label="Séquence", target="Sequence", required=True, choices_key="sequence_id_choices")
