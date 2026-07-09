"""Tests de persistance de la chaîne Scenario (ticket 13) sans backend BDD.

`core.database` est **mocké** : on vérifie que le modèle généré persiste bien un scénario
(insert / get / update, cycle de vie via `statut`) et synchronise ses liens m2m
(compétences visées), sans dépendre d'une base réelle — exécutable en CI (ADR-006).
"""
from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import pytest

from mvc.models import scenario_model as m

_DATA: dict[str, Any] = {
    "titre": "Diagnostic réseau",
    "intention": "Amener l'élève à diagnostiquer une panne réseau simple.",
    "objectifs": None,
    "statut": "brouillon",
    "version": "1.0",
    "referentiel_id": 1,
    "auteur_id": 2,
    "created_at": "2026-07-09 00:00:00",
    "updated_at": "2026-07-09 00:00:00",
}


def test_add_scenario_insere_dans_la_table_scenario(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, Any] = {}

    def fake_insert(sql: str, params: Sequence[Any] = ()) -> int:
        captured["sql"] = sql
        captured["params"] = tuple(params)
        return 42

    monkeypatch.setattr(m, "insert", fake_insert)
    new_id = m.add_scenario(_DATA)

    assert new_id == 42
    assert "INSERT INTO scenario" in captured["sql"]
    assert captured["params"][0] == "Diagnostic réseau"  # Titre en premier
    assert 1 in captured["params"] and 2 in captured["params"]  # FK referentiel/auteur


def test_get_scenario_by_id_interroge_la_table_scenario(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_fetch_one(sql: str, params: Sequence[Any] = ()) -> dict[str, Any] | None:
        assert "FROM scenario" in sql
        return {"Id": params[0], "Titre": "Diagnostic réseau", "Statut": "brouillon"}

    monkeypatch.setattr(m, "fetch_one", fake_fetch_one)
    row = m.get_scenario_by_id(7)
    assert row is not None and row["Id"] == 7


def test_update_scenario_publie_le_statut(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, Any] = {}

    def fake_execute(sql: str, params: Sequence[Any] = (), *, tx: object = None) -> int:
        captured["sql"] = sql
        captured["params"] = tuple(params)
        return 1

    monkeypatch.setattr(m, "execute", fake_execute)
    m.update_scenario(7, {**_DATA, "statut": "publie"})

    assert "UPDATE scenario SET" in captured["sql"]
    assert "publie" in captured["params"]  # cycle de vie : brouillon → publie


def test_sync_competences_remplace_les_liens_du_pivot(monkeypatch: pytest.MonkeyPatch) -> None:
    ops: list[str] = []

    class _Tx:
        def __enter__(self) -> "_Tx":
            return self

        def __exit__(self, *exc: object) -> bool:
            return False

    import core.database.transaction as txmod

    monkeypatch.setattr(txmod, "transaction", lambda: _Tx())

    def fake_execute(sql: str, params: Sequence[Any] = (), *, tx: object = None) -> int:
        ops.append(sql)
        return 1

    monkeypatch.setattr(m, "execute", fake_execute)
    m.sync_scenario_competence_ids(7, [2, 3, 5])

    assert any("DELETE FROM scenario_competence" in s for s in ops)  # purge d'abord
    assert sum("INSERT INTO scenario_competence" in s for s in ops) == 3  # puis 3 liens
