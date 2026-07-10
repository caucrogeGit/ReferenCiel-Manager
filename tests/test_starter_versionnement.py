"""Tests de persistance du versionnement StarterWelcome / VersionStarter (ticket 14).

`core.database` est mocké : on vérifie le motif **identité + versions** (ADR-011) —
une identité `StarterWelcome` et des `VersionStarter` rattachées, avec cycle de vie
`statut`. Sans backend réel : exécutable en CI (ADR-006).
"""
from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import pytest

from mvc.models import starter_welcome_model as sw
from mvc.models import version_starter_model as vs

_STARTER: dict[str, Any] = {
    "identifiant": "welcome-reseau",
    "titre": "Semaine réseau et virtualisation",
    "presentation": None,
    "niveau_classe_id": 1,
    "created_at": "2026-07-10 00:00:00",
    "updated_at": "2026-07-10 00:00:00",
}
_VERSION: dict[str, Any] = {
    "version": "1.0.0",
    "statut": "brouillon",
    "activite_glissante": True,
    "ordre_impose": True,
    "starter_id": 7,
    "created_at": "2026-07-10 00:00:00",
    "updated_at": "2026-07-10 00:00:00",
}


def test_add_starter_welcome_insere_l_identite(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, Any] = {}

    def fake_insert(sql: str, params: Sequence[Any] = ()) -> int:
        captured["sql"] = sql
        captured["params"] = tuple(params)
        return 7

    monkeypatch.setattr(sw, "insert", fake_insert)
    new_id = sw.add_starter_welcome(_STARTER)

    assert new_id == 7
    assert "INSERT INTO starter_welcome" in captured["sql"]
    assert captured["params"][0] == "welcome-reseau"  # Identifiant (stable)


def test_add_version_starter_rattache_a_son_starter(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, Any] = {}

    def fake_insert(sql: str, params: Sequence[Any] = ()) -> int:
        captured["sql"] = sql
        captured["params"] = tuple(params)
        return 1

    monkeypatch.setattr(vs, "insert", fake_insert)
    vs.add_version_starter(_VERSION)

    assert "INSERT INTO version_starter" in captured["sql"]
    assert 7 in captured["params"]  # starter_id : la version reference son identite
    assert "1.0.0" in captured["params"]


def test_update_version_starter_publie_le_statut(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, Any] = {}

    def fake_execute(sql: str, params: Sequence[Any] = (), *, tx: object = None) -> int:
        captured["sql"] = sql
        captured["params"] = tuple(params)
        return 1

    monkeypatch.setattr(vs, "execute", fake_execute)
    vs.update_version_starter(1, {**_VERSION, "statut": "publie"})

    assert "UPDATE version_starter SET" in captured["sql"]
    assert "publie" in captured["params"]  # cycle de vie : brouillon -> publie
