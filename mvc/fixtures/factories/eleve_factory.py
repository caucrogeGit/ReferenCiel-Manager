from typing import Any
from forge_mvc_fixtures import Factory


class EleveFactory(Factory):
    table = "eleve"

    def rows(self, count: int) -> list[dict[str, Any]]:
        # ADR-022 : l'élève est rattaché à une CLASSE (le niveau se déduit de la classe).
        a = self.reference("classe", "Code", "2TNE-A")
        b = self.reference("classe", "Code", "2TNE-B")
        c = self.reference("classe", "Code", "2TNE-C")
        eleve = self.reference("users", "email", "eleve@referenciel.local")
        eleve2 = self.reference("users", "email", "eleve2@referenciel.local")
        return [
            {"Nom": "Dupont", "Prenom": "Marie", "Identifiant": "dupont-marie",
             "DateNaissance": "2009-05-15", "UserId": eleve, "classe_id": a},
            {"Nom": "Martin", "Prenom": "Lucas", "Identifiant": "martin-lucas",
             "DateNaissance": "2009-03-10", "UserId": None, "classe_id": a},
            {"Nom": "Nguyen", "Prenom": "Emma", "Identifiant": "nguyen-emma",
             "DateNaissance": "2009-07-22", "UserId": None, "classe_id": a},
            {"Nom": "Garcia", "Prenom": "Hugo", "Identifiant": "garcia-hugo",
             "DateNaissance": "2009-02-18", "UserId": eleve2, "classe_id": b},
            {"Nom": "Leroy", "Prenom": "Chloé", "Identifiant": "leroy-chloe",
             "DateNaissance": "2009-11-04", "UserId": None, "classe_id": b},
            {"Nom": "Roux", "Prenom": "Nathan", "Identifiant": "roux-nathan",
             "DateNaissance": "2009-06-27", "UserId": None, "classe_id": b},
            {"Nom": "Fabre", "Prenom": "Léa", "Identifiant": "fabre-lea",
             "DateNaissance": "2009-09-12", "UserId": None, "classe_id": c},
            {"Nom": "Blanc", "Prenom": "Tom", "Identifiant": "blanc-tom",
             "DateNaissance": "2009-04-30", "UserId": None, "classe_id": c},
            {"Nom": "Girard", "Prenom": "Inès", "Identifiant": "girard-ines",
             "DateNaissance": "2009-08-07", "UserId": None, "classe_id": c},
        ]
