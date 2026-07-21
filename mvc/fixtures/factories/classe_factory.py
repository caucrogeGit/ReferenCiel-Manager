from typing import Any
from forge_mvc_fixtures import Factory


class ClasseFactory(Factory):
    table = "classe"

    def rows(self, count: int) -> list[dict[str, Any]]:
        # ADR-023 : la classe pointe un formation_niveau (créé par structure.py).
        annee = self.reference("annee_scolaire", "Libelle", "2025-2026")
        fn = self.reference("formation_niveau", "Code", "2TNE-2NDE")
        return [
            {"Code": "2TNE-A", "Libelle": "Seconde TNE A", "annee_scolaire_id": annee, "formation_niveau_id": fn},
            {"Code": "2TNE-B", "Libelle": "Seconde TNE B", "annee_scolaire_id": annee, "formation_niveau_id": fn},
            {"Code": "2TNE-C", "Libelle": "Seconde TNE C", "annee_scolaire_id": annee, "formation_niveau_id": fn},
        ]
