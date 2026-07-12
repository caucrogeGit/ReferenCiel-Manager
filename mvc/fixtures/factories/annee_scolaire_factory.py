from typing import Any
from forge_mvc_fixtures import Factory
class AnneeScolaireFactory(Factory):
    table = "annee_scolaire"
    def rows(self, count: int) -> list[dict[str, Any]]:
        return [{"Libelle": "2025-2026", "DateDebut": "2025-09-01", "DateFin": "2026-07-04", "Active": 1}]
