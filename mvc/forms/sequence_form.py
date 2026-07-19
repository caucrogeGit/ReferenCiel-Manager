from core.forms import Form, BooleanField, RelationField, StringField, TextAreaField


class SequenceForm(Form):
    identifiant = StringField(label="Identifiant", required=True)
    titre = StringField(label="Titre", required=True)
    presentation = StringField(label="Presentation", required=False)
    statut = StringField(label="Statut", required=True)
    activite_glissante = BooleanField(label="Activite glissante")
    ordre_impose = BooleanField(label="Ordre impose")
    # Champs institutionnels (SEQ-02, vademecum voie pro), tous optionnels.
    prerequis = TextAreaField(label="Prérequis", required=False)
    positionnement_progression = TextAreaField(label="Positionnement dans la progression", required=False)
    duree_estimee = StringField(label="Durée estimée", required=False)
    modalites_evaluation = TextAreaField(label="Modalités d'évaluation", required=False)
    niveau_classe_id = RelationField(label="Niveau classe", target="NiveauClasse", required=True, choices_key="niveau_classe_id_choices")
