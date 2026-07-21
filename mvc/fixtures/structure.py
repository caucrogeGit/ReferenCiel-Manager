"""Fixture callable : structure org qui relie le référentiel aux classes (ADR-023).

Le référentiel importé fournit la **formation** (2TNE) mais pas le **niveau de
classe** ni le pont **formation_niveau** dont dépend `classe.formation_niveau_id`.
On les crée ici : niveau « SECONDE_PRO » + formation_niveau « 2TNE-2NDE ». SQL
visible et paramétré ; idempotent sur le niveau (réutilise s'il existe déjà)."""
from forge_mvc_fixtures import Fixture
from core.database import db


class StructureFixture(Fixture):
    tables = ("formation_niveau", "niveau_classe")
    depends_on = ("formation",)

    def load(self) -> None:
        nc = db.fetch_one("SELECT Id FROM niveau_classe WHERE Code = ?", ("SECONDE_PRO",))
        niveau_id = int(nc["Id"]) if nc else db.insert(
            "INSERT INTO niveau_classe (Code, Intitule, CreatedAt, UpdatedAt) "
            "VALUES ('SECONDE_PRO', 'Seconde professionnelle', NOW(), NOW())")
        formation = db.fetch_one("SELECT Id FROM formation WHERE Code = ?", ("2TNE",))
        if formation is None:
            raise RuntimeError("Fixture structure : formation 2TNE introuvable (référentiel non chargé ?).")
        db.insert(
            "INSERT INTO formation_niveau (Code, Libelle, OrdreIndicatif, formation_id, niveau_classe_id, CreatedAt, UpdatedAt) "
            "VALUES ('2TNE-2NDE', '2TNE — Seconde', 1, ?, ?, NOW(), NOW())",
            (int(formation["Id"]), niveau_id))
