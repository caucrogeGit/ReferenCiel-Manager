# pyright: strict
"""Tests du validateur de JSON canonique (ADR-009 : la porte d'entrée).

L'exemple CIEL 2TNE sert de document conforme de référence ; on vérifie ensuite
que les non-conformités (champ requis absent, mauvais type, document non objet)
sont refusées avec des messages localisés par chemin.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from mvc.services.canonical_validator import validate_referentiel_canonical

_ROOT = Path(__file__).resolve().parents[1]
_EXEMPLE = _ROOT / "docs/specs/json-canonique/examples/json-canonique-ciel-2tne.json"


@pytest.fixture()
def canonique() -> dict[str, Any]:
    return json.loads(_EXEMPLE.read_text(encoding="utf-8"))


def test_exemple_de_reference_conforme(canonique: dict[str, Any]) -> None:
    assert validate_referentiel_canonical(canonique) == []


def test_champ_requis_absent_refuse(canonique: dict[str, Any]) -> None:
    del canonique["identifiant"]
    erreurs = validate_referentiel_canonical(canonique)
    assert erreurs
    assert any("identifiant" in e for e in erreurs)


def test_mauvais_type_localise_par_chemin(canonique: dict[str, Any]) -> None:
    canonique["competences"] = "pas-une-liste"
    erreurs = validate_referentiel_canonical(canonique)
    assert erreurs
    assert any(e.startswith("competences :") for e in erreurs)


def test_document_non_objet_refuse_a_la_racine() -> None:
    erreurs = validate_referentiel_canonical([])
    assert erreurs
    assert erreurs[0].startswith("(racine) :")


def test_erreurs_multiples_triees(canonique: dict[str, Any]) -> None:
    del canonique["identifiant"]
    canonique["competences"] = "pas-une-liste"
    erreurs = validate_referentiel_canonical(canonique)
    assert len(erreurs) >= 2
    assert erreurs == sorted(erreurs)
