"""Tests de persistance de la Progression (ticket 18, Bloc B) sans backend BDD.

`core.database` est mocké : on vérifie que l'état réel de l'élève est persisté —
`ProgressionParcours` (par élève et affectation, statut global) et `ProgressionSeance`
(état par seance : non_commence/en_cours/valide/bloque). CI-safe (ADR-006).
"""
from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import pytest

from mvc.models import progression_parcours_model as pe
from mvc.models import progression_seance_model as pp


def _capture_insert(monkeypatch: pytest.MonkeyPatch, module: Any) -> dict[str, Any]:
    captured: dict[str, Any] = {}

    def fake_insert(sql: str, params: Sequence[Any] = ()) -> int:
        captured["sql"] = sql
        captured["params"] = tuple(params)
        return 1

    monkeypatch.setattr(module, "insert", fake_insert)
    return captured


def test_progression_parcours_par_eleve_et_parcours(monkeypatch: pytest.MonkeyPatch) -> None:
    cap = _capture_insert(monkeypatch, pe)
    pe.add_progression_parcours({
        "statut": "en_cours",
        "date_debut": "2026-09-02",
        "eleve_id": 3,
        "parcours_id": 8,
        "created_at": "2026-07-10 00:00:00",
        "updated_at": "2026-07-10 00:00:00",
    })
    assert "INSERT INTO progression_parcours" in cap["sql"]
    assert 3 in cap["params"] and 8 in cap["params"]  # eleve + parcours
    assert "en_cours" in cap["params"]


def test_progression_seance_porte_l_etat_du_seance(monkeypatch: pytest.MonkeyPatch) -> None:
    cap = _capture_insert(monkeypatch, pp)
    pp.add_progression_seance({
        "statut": "valide",  # porte de passage franchie
        "progression_parcours_id": 1,
        "seance_id": 5,
        "created_at": "2026-07-10 00:00:00",
        "updated_at": "2026-07-10 00:00:00",
    })
    assert "INSERT INTO progression_seance" in cap["sql"]
    assert 1 in cap["params"] and 5 in cap["params"]  # progression + seance
    assert "valide" in cap["params"]
