"""Tests de persistance de la Checklist (ticket 19, sous-lot 3) sans backend BDD.

`core.database` est mocké : arbre de **définition** (Checklist → SectionChecklist →
ItemChecklist) et **exécution** (ItemCoche : case cochée par élève et/ou professeur,
dans la progression). CI-safe (ADR-006).
"""
from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import pytest

from mvc.models import item_checklist_model as item
from mvc.models import item_coche_model as coche
from mvc.models import section_checklist_model as section


def _capture_insert(monkeypatch: pytest.MonkeyPatch, module: Any) -> dict[str, Any]:
    captured: dict[str, Any] = {}

    def fake_insert(sql: str, params: Sequence[Any] = ()) -> int:
        captured["sql"] = sql
        captured["params"] = tuple(params)
        return 1

    monkeypatch.setattr(module, "insert", fake_insert)
    return captured


def test_section_rattachee_a_la_checklist(monkeypatch: pytest.MonkeyPatch) -> None:
    cap = _capture_insert(monkeypatch, section)
    section.add_section_checklist({
        "numero": 1, "titre": "Sécurité", "checklist_id": 3,
        "created_at": "2026-07-10 00:00:00", "updated_at": "2026-07-10 00:00:00",
    })
    assert "INSERT INTO section_checklist" in cap["sql"]
    assert 3 in cap["params"] and "Sécurité" in cap["params"]


def test_item_est_un_point_a_verifier(monkeypatch: pytest.MonkeyPatch) -> None:
    cap = _capture_insert(monkeypatch, item)
    item.add_item_checklist({
        "libelle": "Le câble est serti proprement", "section_id": 5,
        "created_at": "2026-07-10 00:00:00", "updated_at": "2026-07-10 00:00:00",
    })
    assert "INSERT INTO item_checklist" in cap["sql"]
    assert 5 in cap["params"]


def test_cochage_par_eleve_et_professeur_dans_la_progression(monkeypatch: pytest.MonkeyPatch) -> None:
    cap = _capture_insert(monkeypatch, coche)
    coche.add_item_coche({
        "coche_eleve": True,
        "coche_professeur": False,
        "item_id": 7,
        "progression_palier_id": 2,
        "created_at": "2026-07-10 00:00:00", "updated_at": "2026-07-10 00:00:00",
    })
    assert "INSERT INTO item_coche" in cap["sql"]
    assert 7 in cap["params"] and 2 in cap["params"]  # item + progression
    assert True in cap["params"] and False in cap["params"]  # coche eleve / prof
