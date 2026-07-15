"""Tests de l'espace élève « Mon parcours » (lecture seule) sans backend BDD.

`core.database` est mocké : on vérifie le **filtrage par compte** (row-level :
`eleve.UserId = ?`), l'assemblage parcours + paliers, et le cas d'un compte non
rattaché à un élève. CI-safe (ADR-006).
"""
from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import pytest

from mvc.models import mon_parcours_model as m


def test_get_eleve_by_user_filtre_sur_le_compte(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, Any] = {}

    def fake_fetch_one(sql: str, params: Sequence[Any] = ()) -> dict[str, Any] | None:
        captured["sql"] = sql
        captured["params"] = tuple(params)
        return {"id": 7, "nom": "Doe", "prenom": "Jane"}

    monkeypatch.setattr(m, "fetch_one", fake_fetch_one)
    eleve = m.get_eleve_by_user(42)

    assert "FROM eleve" in captured["sql"]
    assert "UserId = ?" in captured["sql"]  # sécurité au niveau ligne
    assert captured["params"] == (42,)
    assert eleve is not None and eleve["id"] == 7


def test_mon_parcours_assemble_parcours_et_paliers(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_fetch_one(sql: str, params: Sequence[Any] = ()) -> dict[str, Any] | None:
        return {"id": 7, "nom": "Doe", "prenom": "Jane"}

    calls: list[tuple[str, tuple[Any, ...]]] = []

    def fake_fetch_all(sql: str, params: Sequence[Any] = ()) -> list[dict[str, Any]]:
        calls.append((sql, tuple(params)))
        if "FROM progression_parcours" in sql:
            return [{"progression_id": 3, "statut": "en_cours", "parcours_titre": "P1", "version": "1.0"}]
        return [{"ordre": 1, "titre": "Palier A", "statut": "valide"}]

    monkeypatch.setattr(m, "fetch_one", fake_fetch_one)
    monkeypatch.setattr(m, "fetch_all", fake_fetch_all)

    data = m.mon_parcours(42)

    assert data is not None
    # progressions filtrées sur l'élève résolu (id 7), pas sur le user
    prog_call = next(c for c in calls if "FROM progression_parcours" in c[0])
    assert prog_call[1] == (7,)
    # paliers assemblés sous chaque progression, filtrés sur la progression
    palier_call = next(c for c in calls if "FROM progression_palier" in c[0])
    assert palier_call[1] == (3,)
    assert data["progressions"][0]["paliers"][0]["titre"] == "Palier A"


def test_mon_parcours_compte_non_rattache_renvoie_none(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(m, "fetch_one", lambda sql, params=(): None)

    def _should_not_be_called(sql: str, params: Sequence[Any] = ()) -> list[dict[str, Any]]:
        raise AssertionError("aucune requête de progression si le compte n'est pas lié")

    monkeypatch.setattr(m, "fetch_all", _should_not_be_called)

    assert m.mon_parcours(999) is None
