from typing import Any
from forge_mvc_fixtures import Factory
class AffectationProfesseurClasseFactory(Factory):
    table = "affectation_professeur_classe"
    def rows(self, count: int) -> list[dict[str, Any]]:
        return [{"Role": "Professeur principal",
                 "professeur_id": self.reference("professeur", "Nom", "Bernard"),
                 "classe_id": self.reference("classe", "Code", "2TNE-A"),
                 "annee_scolaire_id": self.reference("annee_scolaire", "Libelle", "2025-2026")}]
