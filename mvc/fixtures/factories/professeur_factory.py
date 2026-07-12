from typing import Any
from forge_mvc_fixtures import Factory
class ProfesseurFactory(Factory):
    table = "professeur"
    def rows(self, count: int) -> list[dict[str, Any]]:
        return [{"Nom": "Bernard", "Prenom": "Julie",
                 "UserId": self.reference("users", "email", "prof@referenciel.local")}]
