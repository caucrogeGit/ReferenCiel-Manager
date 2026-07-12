from typing import Any
from forge_mvc_fixtures import Factory
class InscriptionEleveFactory(Factory):
    table = "inscription_eleve"
    def rows(self, count: int) -> list[dict[str, Any]]:
        annee = self.reference("annee_scolaire", "Libelle", "2025-2026")
        classe = self.reference("classe", "Code", "2TNE-A")
        return [
            {"DateInscription": "2025-09-01", "eleve_id": self.reference("eleve", "Identifiant", ident),
             "classe_id": classe, "annee_scolaire_id": annee}
            for ident in ("dupont-marie", "martin-lucas", "nguyen-emma")
        ]
