"""Tests de la feuille de positionnement (notation par critères, ADR-032/033) sans backend BDD.

`core.database` mocké : on vérifie le find-or-create de l'observation
(`evaluation_activite`), l'upsert/effacement du niveau d'un critère (grille CIEL),
le pointage des indicateurs observés (pivot `indicateur_observe`, coché/décoché), et
l'enregistrement production/aide/appréciation. CI-safe (ADR-006).
"""
from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import pytest

from mvc.models import notation_critere_model as m


class _FakeTx:
    def __enter__(self) -> "_FakeTx":
        return self

    def __exit__(self, *a: object) -> bool:
        return False


def _install(
    monkeypatch: pytest.MonkeyPatch,
    *,
    obs: dict[str, Any] | None,
    critere_existant: dict[str, Any] | None = None,
    indicateurs: list[dict[str, Any]] | None = None,
) -> dict[str, list[Any]]:
    cap: dict[str, list[Any]] = {"insert": [], "execute": []}

    def fake_fetch_one(sql: str, params: Sequence[Any] = (), *, tx: Any = None) -> dict[str, Any] | None:
        if "FROM evaluation_critere" in sql:
            return critere_existant
        if "FROM evaluation_activite" in sql:
            return obs
        return None

    def fake_fetch_all(sql: str, params: Sequence[Any] = (), *, tx: Any = None) -> list[dict[str, Any]]:
        if "FROM indicateur_reussite" in sql:
            return indicateurs or []
        return []

    def fake_insert(sql: str, params: Sequence[Any] = (), *, tx: Any = None) -> int:
        cap["insert"].append((sql, tuple(params)))
        return 50

    def fake_execute(sql: str, params: Sequence[Any] = (), *, tx: Any = None) -> int:
        cap["execute"].append((sql, tuple(params)))
        return 1

    monkeypatch.setattr(m, "transaction", lambda: _FakeTx())
    monkeypatch.setattr(m, "fetch_one", fake_fetch_one)
    monkeypatch.setattr(m, "fetch_all", fake_fetch_all)
    monkeypatch.setattr(m, "insert", fake_insert)
    monkeypatch.setattr(m, "execute", fake_execute)
    return cap


def _sql(cap: dict[str, list[Any]], bucket: str, fragment: str) -> list[tuple[Any, ...]]:
    return [params for sql, params in cap[bucket] if fragment in sql]


def test_positionner_niveau_cree_l_observation_et_upsert(monkeypatch: pytest.MonkeyPatch) -> None:
    cap = _install(monkeypatch, obs=None, critere_existant=None)
    m.positionner_niveau(1, 2, 7, "NIVEAU_3")
    # Observation créée (activité NULL)…
    assert _sql(cap, "insert", "INSERT INTO evaluation_activite") == [(1, 2)]
    # …puis le critère inséré au niveau demandé (eval_id = 50 du fake insert).
    assert _sql(cap, "insert", "INSERT INTO evaluation_critere") == [("NIVEAU_3", 50, 7)]


def test_positionner_niveau_met_a_jour_si_existant(monkeypatch: pytest.MonkeyPatch) -> None:
    cap = _install(monkeypatch, obs={"id": 50}, critere_existant={"id": 88})
    m.positionner_niveau(1, 2, 7, "NIVEAU_4")
    assert _sql(cap, "insert", "INSERT INTO evaluation_critere") == []
    assert any(p == ("NIVEAU_4", 88) for p in _sql(cap, "execute", "UPDATE evaluation_critere"))


def test_positionner_non_observe_efface(monkeypatch: pytest.MonkeyPatch) -> None:
    cap = _install(monkeypatch, obs={"id": 50})
    m.positionner_niveau(1, 2, 7, "NON_OBSERVE")
    assert any(p == (50, 7) for p in _sql(cap, "execute", "DELETE FROM evaluation_critere"))


def test_cocher_indicateurs_coche_et_decoche(monkeypatch: pytest.MonkeyPatch) -> None:
    cap = _install(monkeypatch, obs={"id": 50},
                   indicateurs=[{"id": 11, "libelle": "a"}, {"id": 12, "libelle": "b"}])
    m.maj_indicateurs_observes(1, 2, 7, {11})
    # 11 coché (upsert), 12 décoché (delete), limités aux indicateurs du critère.
    assert any(p == (50, 11) for p in _sql(cap, "execute", "INSERT INTO indicateur_observe"))
    assert any(p == (50, 12) for p in _sql(cap, "execute", "DELETE FROM indicateur_observe"))


def test_enregistrer_notes(monkeypatch: pytest.MonkeyPatch) -> None:
    cap = _install(monkeypatch, obs={"id": 50})
    m.enregistrer_notes(1, 2, "production", "aide", "appréciation")
    assert any(p == ("production", "aide", "appréciation", 50)
               for p in _sql(cap, "execute", "UPDATE evaluation_activite"))
