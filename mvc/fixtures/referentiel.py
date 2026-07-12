"""Fixture callable : import du référentiel ciel-2tne depuis son JSON canonique. ADR-078."""
import json
from pathlib import Path
from forge_mvc_fixtures import Fixture
from mvc.services.referentiel_importer import import_referentiel

_CANON = Path("docs/specs/json-canonique/examples/json-canonique-ciel-2tne.json")


class ReferentielFixture(Fixture):
    tables = ("referentiel_niveau_classe", "formation", "niveau_classe", "pole_activite",
              "activite_professionnelle", "tache", "resultat_attendu", "competence",
              "connaissance", "critere_observable", "indicateur_reussite",
              "famille_competence", "source", "activite_competence", "cc_competence")

    def load(self) -> None:
        import_referentiel(json.loads(_CANON.read_text(encoding="utf-8")))
