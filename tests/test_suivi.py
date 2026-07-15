"""Tests du suivi professeur (ticket 20) sans backend BDD.

`core.database` est mocké : on vérifie que les requêtes d'agrégation ciblent les bonnes
tables et paramètres (affectation → élèves → paliers), sans base réelle. CI-safe (ADR-006).
"""
from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import pytest

from mvc.models import suivi_model as s


def test_list_affectations_agrege_par_affectation(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, Any] = {}

    def fake_fetch_all(sql: str, params: Sequence[Any] = ()) -> list[dict[str, Any]]:
        captured["sql"] = sql
        return [{"id": 1, "nb_progressions": 3}]

    monkeypatch.setattr(s, "fetch_all", fake_fetch_all)
    rows = s.list_affectations()

    assert "FROM affectation_parcours" in captured["sql"]
    assert "progression_parcours" in captured["sql"]
    assert rows[0]["nb_progressions"] == 3


def test_suivi_eleves_filtre_sur_l_affectation(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, Any] = {}

    def fake_fetch_all(sql: str, params: Sequence[Any] = ()) -> list[dict[str, Any]]:
        captured["sql"] = sql
        captured["params"] = tuple(params)
        return []

    monkeypatch.setattr(s, "fetch_all", fake_fetch_all)
    s.suivi_eleves(42)

    assert "FROM progression_parcours" in captured["sql"]
    assert "progression_palier" in captured["sql"]
    assert 42 in captured["params"]  # filtre sur l'affectation
    # les statuts de palier agreges sont passes en parametres (SQL parametre)
    assert "valide" in captured["params"] and "bloque" in captured["params"]
