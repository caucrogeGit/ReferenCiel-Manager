from typing import Any
from forge_mvc_fixtures import Factory
class ClasseFactory(Factory):
    table = "classe"
    def rows(self, count: int) -> list[dict[str, Any]]:
        return [{"Code": "2TNE-A", "Libelle": "Seconde TNE A",
                 "annee_scolaire_id": self.reference("annee_scolaire", "Libelle", "2025-2026"),
                 "niveau_classe_id": self.reference("niveau_classe", "Code", "2TNE")}]
