"""Tests du suivi professeur (ticket 20) sans backend BDD.

`core.database` est mocké : on vérifie que les requêtes d'agrégation ciblent les bonnes
tables et paramètres (classe → élèves → paliers), sans base réelle. CI-safe (ADR-006).
"""
from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import pytest

from mvc.models import suivi_model as s


def test_list_classes_agrege_par_classe(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, Any] = {}

    def fake_fetch_all(sql: str, params: Sequence[Any] = ()) -> list[dict[str, Any]]:
        captured["sql"] = sql
        captured["params"] = tuple(params)
        return [{"id": 1, "nb_progressions": 3}]

    monkeypatch.setattr(s, "fetch_all", fake_fetch_all)
    rows = s.list_classes(7)

    # ADR-022 : les classes du prof via le pivot classe_professeur
    assert "FROM classe_professeur" in captured["sql"]
    assert "progression_parcours" in captured["sql"]
    assert captured["params"] == (7,)  # filtre sur le professeur
    assert rows[0]["nb_progressions"] == 3


def test_suivi_eleves_filtre_sur_la_classe(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, Any] = {}

    def fake_fetch_all(sql: str, params: Sequence[Any] = ()) -> list[dict[str, Any]]:
        captured["sql"] = sql
        captured["params"] = tuple(params)
        return []

    monkeypatch.setattr(s, "fetch_all", fake_fetch_all)
    s.suivi_eleves(42)

    assert "FROM eleve" in captured["sql"]
    assert "e.classe_id = ?" in captured["sql"]
    assert "progression_parcours" in captured["sql"]
    assert "progression_palier" in captured["sql"]
    assert 42 in captured["params"]  # filtre sur la classe
    # les statuts de palier agreges sont passes en parametres (SQL parametre)
    assert "valide" in captured["params"] and "bloque" in captured["params"]
