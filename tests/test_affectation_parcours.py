"""Tests de persistance de l'AffectationParcours (ticket 17, Bloc B) sans backend BDD.

`core.database` est mocké : on vérifie qu'une affectation référence une **version de
parcours** (figée, publiée), une classe et un professeur, et que le **sous-ensemble
d'élèves** (m2m optionnel) se synchronise. Sans backend réel : exécutable en CI (ADR-006).
"""
from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import pytest

from mvc.models import affectation_parcours_model as ap

_DATA: dict[str, Any] = {
    "date_affectation": "2026-09-01",
    "statut": "active",
    "version_parcours_id": 4,  # version publiee figee
    "classe_id": 2,
    "professeur_id": 1,
    "created_at": "2026-07-10 00:00:00",
    "updated_at": "2026-07-10 00:00:00",
}


def test_affectation_reference_une_version_figee(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, Any] = {}

    def fake_insert(sql: str, params: Sequence[Any] = ()) -> int:
        captured["sql"] = sql
        captured["params"] = tuple(params)
        return 1

    monkeypatch.setattr(ap, "insert", fake_insert)
    ap.add_affectation_parcours(_DATA)

    assert "INSERT INTO affectation_parcours" in captured["sql"]
    # version figee + classe + prof presents
    assert 4 in captured["params"] and 2 in captured["params"] and 1 in captured["params"]
    assert "active" in captured["params"]


def test_sync_du_sous_ensemble_d_eleves(monkeypatch: pytest.MonkeyPatch) -> None:
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

    monkeypatch.setattr(ap, "execute", fake_execute)
    ap.sync_affectation_parcours_eleve_ids(1, [10, 11])

    assert any("DELETE FROM affectation_parcours_eleve" in s for s in ops)  # remplace
    assert sum("INSERT INTO affectation_parcours_eleve" in s for s in ops) == 2  # 2 eleves
