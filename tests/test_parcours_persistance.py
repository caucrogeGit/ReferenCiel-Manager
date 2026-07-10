"""Tests de persistance de la chaîne Parcours (tickets 15-16) sans backend BDD.

`core.database` est mocké : on vérifie la **dérivation** (Parcours → VersionStarter),
le **versionnement** (VersionParcours, ADR-011) et le **découpage** (Palier →
VersionParcours). Sans backend réel : exécutable en CI (ADR-006).
"""
from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import pytest

from mvc.models import palier_model as pal
from mvc.models import parcours_model as par
from mvc.models import version_parcours_model as vpar


def _capture_insert(monkeypatch: pytest.MonkeyPatch, module: Any) -> dict[str, Any]:
    captured: dict[str, Any] = {}

    def fake_insert(sql: str, params: Sequence[Any] = ()) -> int:
        captured["sql"] = sql
        captured["params"] = tuple(params)
        return 1

    monkeypatch.setattr(module, "insert", fake_insert)
    return captured


def test_parcours_derive_d_une_version_starter(monkeypatch: pytest.MonkeyPatch) -> None:
    cap = _capture_insert(monkeypatch, par)
    par.add_parcours({
        "titre": "Parcours réseau 2TNE",
        "version_starter_id": 3,  # dérivation d'une version de starter
        "created_at": "2026-07-10 00:00:00",
        "updated_at": "2026-07-10 00:00:00",
    })
    assert "INSERT INTO parcours" in cap["sql"]
    assert 3 in cap["params"]  # version_starter_id : le parcours dérive du starter


def test_version_parcours_rattache_au_parcours(monkeypatch: pytest.MonkeyPatch) -> None:
    cap = _capture_insert(monkeypatch, vpar)
    vpar.add_version_parcours({
        "version": "1.0.0",
        "statut": "brouillon",
        "parcours_id": 5,
        "created_at": "2026-07-10 00:00:00",
        "updated_at": "2026-07-10 00:00:00",
    })
    assert "INSERT INTO version_parcours" in cap["sql"]
    assert 5 in cap["params"] and "1.0.0" in cap["params"]


def test_palier_rattache_a_la_version_parcours(monkeypatch: pytest.MonkeyPatch) -> None:
    cap = _capture_insert(monkeypatch, pal)
    pal.add_palier({
        "ordre": 1,
        "titre": "Câblage",
        "theme": None,
        "production_attendue": None,
        "dossier_technique_fichier": "dt-cablage.pdf",
        "version_parcours_id": 9,  # decoupage rattache a la version de parcours
        "created_at": "2026-07-10 00:00:00",
        "updated_at": "2026-07-10 00:00:00",
    })
    assert "INSERT INTO palier" in cap["sql"]
    assert 9 in cap["params"] and 1 in cap["params"]  # version_parcours_id + Ordre
