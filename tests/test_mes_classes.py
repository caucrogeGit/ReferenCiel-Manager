"""Tests de l'espace professeur « Mes classes » (ticket 07) sans backend BDD.

`core.database` est mocké : on vérifie que les requêtes ciblent les bonnes tables
et paramètres (professeur → affectations → élèves inscrits), le filtrage par compte
(`professeur.UserId`) et le cas du compte non rattaché. CI-safe (ADR-006).
"""
from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import pytest

from mvc.models import mes_classes_model as m


def test_get_professeur_by_user_filtre_sur_le_compte(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, Any] = {}

    def fake_fetch_one(sql: str, params: Sequence[Any] = ()) -> dict[str, Any] | None:
        captured["sql"] = sql
        captured["params"] = tuple(params)
        return {"id": 7, "nom": "Durand", "prenom": "Alex"}

    monkeypatch.setattr(m, "fetch_one", fake_fetch_one)
    row = m.get_professeur_by_user(42)

    assert "FROM professeur" in captured["sql"]
    assert "UserId = ?" in captured["sql"]  # sécurité au niveau ligne (row-level)
    assert captured["params"] == (42,)
    assert row is not None and row["id"] == 7


def test_mes_affectations_joint_classe_et_compte_les_eleves(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, Any] = {}

    def fake_fetch_all(sql: str, params: Sequence[Any] = ()) -> list[dict[str, Any]]:
        captured["sql"] = sql
        captured["params"] = tuple(params)
        return [{"affectation_id": 1, "classe_id": 3, "annee_scolaire_id": 5, "nb_eleves": 2}]

    monkeypatch.setattr(m, "fetch_all", fake_fetch_all)
    rows = m.mes_affectations(7)

    assert "FROM affectation_professeur_classe" in captured["sql"]
    assert "JOIN classe" in captured["sql"]
    assert "inscription_eleve" in captured["sql"]
    assert captured["params"] == (7,)  # filtre sur le professeur
    assert rows[0]["nb_eleves"] == 2


def test_eleves_de_classe_filtre_classe_et_annee(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, Any] = {}

    def fake_fetch_all(sql: str, params: Sequence[Any] = ()) -> list[dict[str, Any]]:
        captured["sql"] = sql
        captured["params"] = tuple(params)
        return []

    monkeypatch.setattr(m, "fetch_all", fake_fetch_all)
    m.eleves_de_classe(3, 5)

    assert "FROM inscription_eleve" in captured["sql"]
    assert "JOIN eleve" in captured["sql"]
    assert captured["params"] == (3, 5)  # classe puis année


def test_mes_classes_compose_professeur_affectations_et_eleves(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        m, "get_professeur_by_user", lambda _uid: {"id": 7, "nom": "Durand", "prenom": "Alex"}
    )
    monkeypatch.setattr(
        m,
        "mes_affectations",
        lambda _pid: [{"affectation_id": 1, "classe_id": 3, "annee_scolaire_id": 5}],
    )
    monkeypatch.setattr(
        m, "eleves_de_classe", lambda _cid, _aid: [{"id": 9, "nom": "Petit", "prenom": "Sam"}]
    )

    data = m.mes_classes(42)

    assert data is not None
    assert data["professeur"]["id"] == 7
    assert data["affectations"][0]["eleves"][0]["nom"] == "Petit"


def test_mes_classes_compte_non_lie_renvoie_none(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(m, "get_professeur_by_user", lambda _uid: None)

    assert m.mes_classes(42) is None
