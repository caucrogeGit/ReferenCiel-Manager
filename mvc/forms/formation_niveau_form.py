from core.forms import Form, IntegerField, RelationField, StringField


class FormationNiveauForm(Form):
    code = StringField(label="Code", required=True)
    libelle = StringField(label="Libelle", required=True)
    ordre_indicatif = IntegerField(label="Ordre indicatif", required=True)
    formation_id = RelationField(label="Formation", target="Formation", required=True, choices_key="formation_id_choices")
    niveau_classe_id = RelationField(label="Niveau classe", target="NiveauClasse", required=True, choices_key="niveau_classe_id_choices")
