"""Tests de persistance de l'évaluation par critères (ticket 21) sans backend BDD.

`core.database` est mocké : le prof évalue le travail d'un élève (`EvaluationActivite`
= ProgressionSeance + Activite + Professeur) et attribue un **niveau** par critère
observable (`EvaluationCritere`, barème 4 niveaux). CI-safe (ADR-006).
"""
from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import pytest

from mvc.models import evaluation_activite_model as ea
from mvc.models import evaluation_critere_model as ec


def _capture_insert(monkeypatch: pytest.MonkeyPatch, module: Any) -> dict[str, Any]:
    captured: dict[str, Any] = {}

    def fake_insert(sql: str, params: Sequence[Any] = ()) -> int:
        captured["sql"] = sql
        captured["params"] = tuple(params)
        return 1

    monkeypatch.setattr(module, "insert", fake_insert)
    return captured


def test_evaluation_activite_dans_le_contexte_eleve(monkeypatch: pytest.MonkeyPatch) -> None:
    cap = _capture_insert(monkeypatch, ea)
    ea.add_evaluation_activite({
        "date_evaluation": "2026-09-06 09:00:00",
        "appreciation": "Travail soigné.",
        "progression_seance_id": 6,
        "activite_id": 2,
        "professeur_id": 1,
        "created_at": "2026-07-10 00:00:00", "updated_at": "2026-07-10 00:00:00",
    })
    assert "INSERT INTO evaluation_activite" in cap["sql"]
    # contexte : progression (eleve+seance) + activite + prof evaluateur
    assert 6 in cap["params"] and 2 in cap["params"] and 1 in cap["params"]


def test_evaluation_critere_attribue_un_niveau(monkeypatch: pytest.MonkeyPatch) -> None:
    cap = _capture_insert(monkeypatch, ec)
    ec.add_evaluation_critere({
        "niveau": "acquis",  # bareme 4 niveaux
        "evaluation_activite_id": 3,
        "critere_id": 8,  # critere observable du referentiel
        "created_at": "2026-07-10 00:00:00", "updated_at": "2026-07-10 00:00:00",
    })
    assert "INSERT INTO evaluation_critere" in cap["sql"]
    assert "acquis" in cap["params"]
    assert 3 in cap["params"] and 8 in cap["params"]  # evaluation + critere
