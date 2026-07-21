"""Fixture callable : le pont formation_niveau pour la démo (ADR-023).

La **formation** ET le **niveau_classe** viennent du canonique importé
(referentiel_importer). Le **pont** `formation_niveau` (formation × niveau, avec un
ordre) n'est PAS porté par le canonique : c'est une donnée d'établissement. Dans
l'application, elle se saisit via le **CRUD admin `/formation_niveau`** ; ici, on la
sème simplement pour la démo (comme classe.sql sème des classes). `classe.formation_niveau_id`
en dépend. SQL visible et paramétré.
"""
from forge_mvc_fixtures import Fixture
from core.database import db


class StructureFixture(Fixture):
    tables = ("formation_niveau",)
    depends_on = ("formation", "niveau_classe")

    def load(self) -> None:
        formation = db.fetch_one("SELECT Id FROM formation WHERE Code = ?", ("2TNE",))
        niveau = db.fetch_one("SELECT Id FROM niveau_classe WHERE Code = ?", ("SECONDE_PRO",))
        if formation is None or niveau is None:
            raise RuntimeError(
                "Fixture structure : formation 2TNE / niveau SECONDE_PRO introuvables "
                "(référentiel 2tne-ciel non importé ?)."
            )
        db.insert(
            "INSERT INTO formation_niveau (Code, Libelle, OrdreIndicatif, formation_id, niveau_classe_id, CreatedAt, UpdatedAt) "
            "VALUES ('2TNE-2NDE', '2TNE — Seconde', 1, ?, ?, NOW(), NOW())",
            (int(formation["Id"]), int(niveau["Id"])),
        )
