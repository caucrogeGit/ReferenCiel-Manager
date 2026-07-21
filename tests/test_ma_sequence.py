"""Tests de l'espace élève « Mon sequence » (lecture seule) sans backend BDD.

`core.database` est mocké : on vérifie le **filtrage par compte** (row-level :
`eleve.UserId = ?`), l'assemblage sequence + seances, et le cas d'un compte non
rattaché à un élève. CI-safe (ADR-006).
"""
from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import pytest

from mvc.models import ma_sequence_model as m


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


def test_ma_sequence_assemble_sequence_et_seances(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_fetch_one(sql: str, params: Sequence[Any] = ()) -> dict[str, Any] | None:
        return {"id": 7, "nom": "Doe", "prenom": "Jane"}

    calls: list[tuple[str, tuple[Any, ...]]] = []

    def fake_fetch_all(sql: str, params: Sequence[Any] = ()) -> list[dict[str, Any]]:
        calls.append((sql, tuple(params)))
        if "FROM progression_sequence" in sql:
            return [{"progression_id": 3, "statut": "en_cours", "sequence_titre": "P1", "version": "1.0"}]
        return [{"ordre": 1, "titre": "Seance A", "statut": "valide"}]

    monkeypatch.setattr(m, "fetch_one", fake_fetch_one)
    monkeypatch.setattr(m, "fetch_all", fake_fetch_all)

    data = m.ma_sequence(42)

    assert data is not None
    # progressions filtrées sur l'élève résolu (id 7), pas sur le user
    prog_call = next(c for c in calls if "FROM progression_sequence" in c[0])
    assert prog_call[1] == (7,)
    # seances assemblés sous chaque progression, filtrés sur la progression
    seance_call = next(c for c in calls if "FROM progression_seance" in c[0])
    assert seance_call[1] == (3,)
    assert data["progressions"][0]["seances"][0]["titre"] == "Seance A"


def test_ma_sequence_compte_non_rattache_renvoie_none(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(m, "fetch_one", lambda sql, params=(): None)

    def _should_not_be_called(sql: str, params: Sequence[Any] = ()) -> list[dict[str, Any]]:
        raise AssertionError("aucune requête de progression si le compte n'est pas lié")

    monkeypatch.setattr(m, "fetch_all", _should_not_be_called)

    assert m.ma_sequence(999) is None


def test_mes_bilans_ne_liste_que_les_publies_de_l_eleve(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, Any] = {}

    def fake_fetch_all(sql: str, params: Sequence[Any] = ()) -> list[dict[str, Any]]:
        captured["sql"] = sql
        captured["params"] = tuple(params)
        return []

    monkeypatch.setattr(m, "fetch_all", fake_fetch_all)
    m.mes_bilans(7)

    assert "b.eleve_id = ?" in captured["sql"]  # sécurité au niveau ligne
    assert "b.Statut = 'publie'" in captured["sql"]  # ni brouillon ni archive
    assert captured["params"] == (7,)


def test_get_mon_bilan_filtre_eleve_et_publie_et_deserialise(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, Any] = {}

    def fake_fetch_one(sql: str, params: Sequence[Any] = ()) -> dict[str, Any] | None:
        captured["sql"] = sql
        captured["params"] = tuple(params)
        return {"id": 5, "appreciation": "ok", "date_bilan": "2026-07-21",
                "synthese": '[{"competence_code": "C01", "niveau_arrete": "NIVEAU_3"}]',
                "prof_nom": "Bernard", "prof_prenom": "Julie"}

    monkeypatch.setattr(m, "fetch_one", fake_fetch_one)
    bilan = m.get_mon_bilan(7, 5)

    # Filtré sur le bilan, l'élève ET le statut publié (un élève ne lit pas le bilan d'un autre).
    assert "b.Id = ?" in captured["sql"] and "b.eleve_id = ?" in captured["sql"]
    assert "b.Statut = 'publie'" in captured["sql"]
    assert captured["params"] == (5, 7)
    # Synthèse désérialisée.
    assert bilan is not None
    assert isinstance(bilan["synthese"], list)
    assert bilan["synthese"][0]["niveau_arrete"] == "NIVEAU_3"


def test_get_mon_bilan_absent_renvoie_none(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(m, "fetch_one", lambda sql, params=(): None)
    assert m.get_mon_bilan(7, 999) is None
