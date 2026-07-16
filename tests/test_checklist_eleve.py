"""Tests de la saisie élève « cocher la checklist » sans backend BDD.

`core.database` mocké : on vérifie l'upsert de `CocheEleve` sur TOUS les items
(cochés → 1, décochés → 0), la préservation de `CocheProfesseur`, et le contrôle
d'appartenance (palier d'autrui → None, aucune écriture). CI-safe (ADR-006).
"""
from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import pytest

from mvc.models import checklist_eleve_model as m


class _FakeTx:
    def __enter__(self) -> "_FakeTx":
        return self

    def __exit__(self, *a: object) -> bool:
        return False


def _install(monkeypatch: pytest.MonkeyPatch, *, palier: dict[str, Any] | None) -> list[tuple[str, tuple[Any, ...]]]:
    calls: list[tuple[str, tuple[Any, ...]]] = []

    def fake_fetch_one(sql: str, params: Sequence[Any] = ()) -> dict[str, Any] | None:
        if "FROM progression_palier pp" in sql:
            return palier
        if "FROM checklist WHERE seance_id" in sql:
            return {"id": 3}
        return None

    def fake_fetch_all(sql: str, params: Sequence[Any] = ()) -> list[dict[str, Any]]:
        if "FROM item_checklist i" in sql:
            return [{"id": 10}, {"id": 11}, {"id": 12}]
        return []

    def fake_execute(sql: str, params: Sequence[Any] = (), *, tx: Any = None) -> int:
        calls.append((sql, tuple(params)))
        return 1

    monkeypatch.setattr(m, "transaction", lambda: _FakeTx())
    monkeypatch.setattr(m, "fetch_one", fake_fetch_one)
    monkeypatch.setattr(m, "fetch_all", fake_fetch_all)
    monkeypatch.setattr(m, "execute", fake_execute)
    return calls


def test_coche_tous_les_items_et_preserve_le_prof(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = _install(monkeypatch, palier={"progression_palier_id": 1, "seance_id": 5, "palier_titre": "P"})

    res = m.enregistrer_coches(1, 42, {10, 12})

    assert res == {"items": 3, "coches": 2}
    assert len(calls) == 3  # upsert pour chaque item de la checklist
    # (valeur CocheEleve, item_id) — 10 et 12 cochés, 11 décoché
    paires = {(c[1][0], c[1][1]) for c in calls}
    assert paires == {(1, 10), (0, 11), (1, 12)}
    # upsert idempotent qui ne touche jamais CocheProfesseur
    assert all("ON DUPLICATE KEY UPDATE CocheEleve = VALUES(CocheEleve)" in c[0] for c in calls)
    assert all("CocheProfesseur = VALUES" not in c[0] for c in calls)


def test_palier_d_autrui_renvoie_none(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = _install(monkeypatch, palier=None)
    assert m.enregistrer_coches(1, 42, {10}) is None
    assert calls == []  # aucune écriture
