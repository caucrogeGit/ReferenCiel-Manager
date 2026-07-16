from core.forms import Form, BooleanField, RelationField


class ItemCocheForm(Form):
    coche_eleve = BooleanField(label="Coche eleve")
    coche_professeur = BooleanField(label="Coche professeur")
    item_id = RelationField(label="Item", target="ItemChecklist", required=True, choices_key="item_id_choices")
    progression_seance_id = RelationField(label="Progression séance", target="ProgressionSeance", required=True, choices_key="progression_seance_id_choices")
