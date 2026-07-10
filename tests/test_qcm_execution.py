"""Tests de persistance de l'exécution QCM (ticket 19, sous-lot 2) sans backend BDD.

`core.database` est mocké : une `TentativeQCM` s'inscrit dans la `ProgressionPalier`
de l'élève (score, validée) et ses `ReponseQCM` figent la justesse (`est_correcte`)
au moment de la soumission. CI-safe (ADR-006).
"""
from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import pytest

from mvc.models import reponse_qcm_model as rep
from mvc.models import tentative_qcm_model as tent


def _capture_insert(monkeypatch: pytest.MonkeyPatch, module: Any) -> dict[str, Any]:
    captured: dict[str, Any] = {}

    def fake_insert(sql: str, params: Sequence[Any] = ()) -> int:
        captured["sql"] = sql
        captured["params"] = tuple(params)
        return 1

    monkeypatch.setattr(module, "insert", fake_insert)
    return captured


def test_tentative_dans_la_progression_palier(monkeypatch: pytest.MonkeyPatch) -> None:
    cap = _capture_insert(monkeypatch, tent)
    tent.add_tentative_qcm({
        "numero_tentative": 2,
        "score": 100,
        "validee": True,  # porte de passage franchie
        "date_tentative": "2026-09-03 10:00:00",
        "progression_palier_id": 6,
        "created_at": "2026-07-10 00:00:00",
        "updated_at": "2026-07-10 00:00:00",
    })
    assert "INSERT INTO tentative_qcm" in cap["sql"]
    assert 6 in cap["params"] and 2 in cap["params"]  # progression_palier + numero
    assert True in cap["params"] and 100 in cap["params"]


def test_reponse_fige_la_justesse(monkeypatch: pytest.MonkeyPatch) -> None:
    cap = _capture_insert(monkeypatch, rep)
    rep.add_reponse_qcm({
        "est_correcte": True,  # snapshot au moment de la soumission
        "tentative_id": 1,
        "question_id": 4,
        "choix_id": 9,
        "created_at": "2026-07-10 00:00:00",
        "updated_at": "2026-07-10 00:00:00",
    })
    assert "INSERT INTO reponse_qcm" in cap["sql"]
    assert 1 in cap["params"] and 4 in cap["params"] and 9 in cap["params"]
    assert True in cap["params"]  # est_correcte fige
