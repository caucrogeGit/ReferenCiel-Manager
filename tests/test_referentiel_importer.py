# pyright: strict
"""Tests de l'importeur de référentiel (ticket 11) sans backend BDD.

`core.database.db` est **mocké** : on vérifie l'orchestration (mapping des id/codes
locaux, comptes insérés, upsert par identifiant, best-effort) sur l'exemple CIEL 2TNE,
sans dépendre d'une base réelle — donc exécutable en CI (ADR-006).
"""
from __future__ import annotations

import json
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import pytest

from mvc.services import referentiel_importer as imp
from mvc.services.canonical_validator import validate_referentiel_canonical

_ROOT = Path(__file__).resolve().parents[1]
_EXEMPLE = _ROOT / "docs/specs/json-canonique/examples/json-canonique-ciel-2tne.json"

# Comptes attendus pour l'exemple CIEL 2TNE (source de vérité du test).
_ATTENDU = {
    "sources": 2, "poles": 3, "competences": 8, "criteres": 9, "activites": 5,
    "taches": 19, "resultats": 7, "familles": 9, "indicateurs": 1,
    "activite_competence": 14, "cc_competence": 2,
}
# ADR-022 option A : seuls les indicateurs d'origine 'critere' sont importés
# (ici ind-2). Les amorces resultat_attendu / reformulation ne le sont plus.
_TOTAL = 79


class _FakeDb:
    """Enregistre les requêtes et simule des `Id` auto-incrémentés."""

    def __init__(self, *, referentiel_existe: bool = False) -> None:
        self._seq = 0
        self._referentiel_existe = referentiel_existe
        self.inserts: list[str] = []
        self.executes: list[str] = []

    def fetch_one(self, sql: str, params: Sequence[Any] = (), *, tx: object = None) -> dict[str, Any] | None:
        if self._referentiel_existe and "referentiel_niveau_classe WHERE Identifiant" in sql:
            return {"Id": 1}
        return None

    def insert(self, sql: str, params: Sequence[Any] = (), *, tx: object = None) -> int:
        self._seq += 1
        self.inserts.append(sql)
        return self._seq

    def execute(self, sql: str, params: Sequence[Any] = (), *, tx: object = None) -> int:
        self.executes.append(sql)
        return 0


@pytest.fixture
def canonical() -> dict[str, Any]:
    return json.loads(_EXEMPLE.read_text(encoding="utf-8"))


def _brancher(monkeypatch: pytest.MonkeyPatch, fake: _FakeDb) -> None:
    monkeypatch.setattr(imp.db, "fetch_one", fake.fetch_one)
    monkeypatch.setattr(imp.db, "insert", fake.insert)
    monkeypatch.setattr(imp.db, "execute", fake.execute)


def test_import_frais_compte_et_mappe(monkeypatch: pytest.MonkeyPatch, canonical: dict[str, Any]) -> None:
    """Un import initial insère tous les objets, sans erreur, et n'est pas un remplacement."""
    fake = _FakeDb(referentiel_existe=False)
    _brancher(monkeypatch, fake)

    rapport = imp.import_referentiel(canonical)

    assert rapport.identifiant == "ciel-2tne"
    assert rapport.remplacement is False
    assert rapport.erreurs == []
    assert rapport.inseres == _ATTENDU
    assert sum(rapport.inseres.values()) == _TOTAL
    assert rapport.ok


def test_reimport_est_un_remplacement_avec_purge(monkeypatch: pytest.MonkeyPatch, canonical: dict[str, Any]) -> None:
    """Ré-importer un identifiant existant purge le contenu (DELETE) puis ré-insère."""
    fake = _FakeDb(referentiel_existe=True)
    _brancher(monkeypatch, fake)

    rapport = imp.import_referentiel(canonical)

    assert rapport.remplacement is True
    assert rapport.referentiel_id == 1
    assert rapport.erreurs == []
    assert rapport.inseres == _ATTENDU
    # La purge a bien émis des DELETE avant la ré-insertion.
    assert any(sql.strip().upper().startswith("DELETE") for sql in fake.executes)


def test_validateur_accepte_exemple_et_refuse_document_casse(canonical: dict[str, Any]) -> None:
    """Le validateur laisse passer l'exemple conforme et refuse un document incomplet."""
    assert validate_referentiel_canonical(canonical) == []
    erreurs = validate_referentiel_canonical({"type": "referentiel_niveau_classe"})
    assert erreurs  # au moins une propriété requise manquante
