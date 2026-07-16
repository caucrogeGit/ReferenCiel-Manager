"""Tests de persistance Activité + DépôtEleve (ticket 19, sous-lot 4) sans backend BDD.

`core.database` est mocké : `Activite` (lieu d'observation, par seance) et `DepotEleve`
(l'élève rend un travail : un fichier, rattaché à sa progression et à l'activité). CI-safe.
"""
from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import pytest

from mvc.models import activite_model as act
from mvc.models import depot_eleve_model as depot


def _capture_insert(monkeypatch: pytest.MonkeyPatch, module: Any) -> dict[str, Any]:
    captured: dict[str, Any] = {}

    def fake_insert(sql: str, params: Sequence[Any] = ()) -> int:
        captured["sql"] = sql
        captured["params"] = tuple(params)
        return 1

    monkeypatch.setattr(module, "insert", fake_insert)
    return captured


def test_activite_rattachee_a_un_seance(monkeypatch: pytest.MonkeyPatch) -> None:
    cap = _capture_insert(monkeypatch, act)
    act.add_activite({
        "objectif": "Sertir un câble RJ45",
        "fichier": None,
        "seance_id": 4,
        "created_at": "2026-07-10 00:00:00", "updated_at": "2026-07-10 00:00:00",
    })
    assert "INSERT INTO activite" in cap["sql"]
    assert 4 in cap["params"]


def test_depot_rend_un_fichier_dans_la_progression(monkeypatch: pytest.MonkeyPatch) -> None:
    cap = _capture_insert(monkeypatch, depot)
    depot.add_depot_eleve({
        "fichier": "depots/rendu-eleve-3.pdf",
        "commentaire": None,
        "date_depot": "2026-09-05 14:30:00",
        "progression_palier_id": 6,
        "activite_id": 2,
        "created_at": "2026-07-10 00:00:00", "updated_at": "2026-07-10 00:00:00",
    })
    assert "INSERT INTO depot_eleve" in cap["sql"]
    assert "depots/rendu-eleve-3.pdf" in cap["params"]
    assert 6 in cap["params"] and 2 in cap["params"]  # progression + activite
