"""Fixture callable : bilan élève (valeur calculée par agrégation). ADR-078."""
from typing import Any
from forge_mvc_fixtures import Fixture
from core.database import db
from mvc.models.bilan_eleve_model import creer_bilan


def _id(row: "dict[str, Any] | None") -> int:
    if row is None:
        raise RuntimeError("Fixture bilan : progression/professeur introuvable.")
    return int(row["Id"])


class BilanFixture(Fixture):
    tables = ("bilan_eleve",)
    depends_on = ("progression_sequence", "evaluation_critere", "professeur")

    def load(self) -> None:
        pe = _id(db.fetch_one(
            "SELECT pe.Id FROM progression_sequence pe JOIN eleve e ON e.Id = pe.eleve_id "
            "WHERE e.Identifiant = ?", ("dupont-marie",)))
        prof = _id(db.fetch_one("SELECT Id FROM professeur WHERE Nom = ?", ("Bernard",)))
        creer_bilan(progression_sequence_id=pe, professeur_id=prof,
                    appreciation="Élève sérieux, bonne progression sur le câblage.", statut="publie")
