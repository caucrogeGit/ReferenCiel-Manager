"""Tests de persistance de la définition QCM (ticket 19, sous-lot 1) sans backend BDD.

`core.database` est mocké : on vérifie l'arbre de définition QCM → QuestionQCM → ChoixQCM
(corrigé fusionné via `bonne_reponse`), rattaché à un Palier. CI-safe (ADR-006).
"""
from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import pytest

from mvc.models import choix_qcm_model as choix
from mvc.models import qcm_model as qcm
from mvc.models import question_qcm_model as question


def _capture_insert(monkeypatch: pytest.MonkeyPatch, module: Any) -> dict[str, Any]:
    captured: dict[str, Any] = {}

    def fake_insert(sql: str, params: Sequence[Any] = ()) -> int:
        captured["sql"] = sql
        captured["params"] = tuple(params)
        return 1

    monkeypatch.setattr(module, "insert", fake_insert)
    return captured


def test_qcm_rattache_a_un_palier(monkeypatch: pytest.MonkeyPatch) -> None:
    cap = _capture_insert(monkeypatch, qcm)
    qcm.add_qcm({
        "format_reponse": None,
        "seuil_validation": "100%",
        "palier_id": 5,
        "created_at": "2026-07-10 00:00:00",
        "updated_at": "2026-07-10 00:00:00",
    })
    assert "INSERT INTO qcm" in cap["sql"]
    assert 5 in cap["params"] and "100%" in cap["params"]


def test_question_porte_le_corrige(monkeypatch: pytest.MonkeyPatch) -> None:
    cap = _capture_insert(monkeypatch, question)
    question.add_question_qcm({
        "numero": 1,
        "enonce": "Quelle topologie ?",
        "bonne_reponse": "B",  # corrige fusionne dans la definition
        "qcm_id": 2,
        "created_at": "2026-07-10 00:00:00",
        "updated_at": "2026-07-10 00:00:00",
    })
    assert "INSERT INTO question_qcm" in cap["sql"]
    assert "B" in cap["params"] and 2 in cap["params"]


def test_choix_rattache_a_la_question(monkeypatch: pytest.MonkeyPatch) -> None:
    cap = _capture_insert(monkeypatch, choix)
    choix.add_choix_qcm({
        "lettre": "B",
        "texte": "Étoile",
        "question_id": 7,
        "created_at": "2026-07-10 00:00:00",
        "updated_at": "2026-07-10 00:00:00",
    })
    assert "INSERT INTO choix_qcm" in cap["sql"]
    assert "B" in cap["params"] and 7 in cap["params"]
