from typing import Any
from forge_mvc_fixtures import Factory
class EleveFactory(Factory):
    table = "eleve"
    def rows(self, count: int) -> list[dict[str, Any]]:
        return [
            {"Nom": "Dupont", "Prenom": "Marie", "Identifiant": "dupont-marie",
             "DateNaissance": "2009-05-15",
             "UserId": self.reference("users", "email", "eleve@referenciel.local")},
            {"Nom": "Martin", "Prenom": "Lucas", "Identifiant": "martin-lucas",
             "DateNaissance": "2009-03-10", "UserId": None},
            {"Nom": "Nguyen", "Prenom": "Emma", "Identifiant": "nguyen-emma",
             "DateNaissance": "2009-07-22", "UserId": None},
        ]
