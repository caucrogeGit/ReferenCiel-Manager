"""Tests de l'évaluation professeur sans backend BDD.

`core.database` mocké : on vérifie la validation du statut de palier (valeur
contrôlée), et le cochage `CocheProfesseur` (upsert qui ne touche pas
`CocheEleve`). CI-safe (ADR-006).
"""
from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import pytest

from mvc.models import evaluation_prof_model as m


class _FakeTx:
    def __enter__(self) -> "_FakeTx":
        return self

    def __exit__(self, *a: object) -> bool:
        return False


def test_set_palier_statut_refuse_valeur_invalide(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[tuple[str, tuple[Any, ...]]] = []
    monkeypatch.setattr(m, "execute", lambda sql, params=(): calls.append((sql, tuple(params))) or 1)

    assert m.set_palier_statut(3, "n_importe_quoi") is False
    assert calls == []  # aucune écriture pour un statut hors liste


def test_set_palier_statut_pose_un_statut_valide(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[tuple[str, tuple[Any, ...]]] = []
    monkeypatch.setattr(m, "execute", lambda sql, params=(): calls.append((sql, tuple(params))) or 1)

    assert m.set_palier_statut(3, "valide") is True
    assert len(calls) == 1
    assert "UPDATE progression_palier SET Statut" in calls[0][0]
    assert calls[0][1] == ("valide", 3)


def test_coches_prof_upsert_sans_toucher_l_eleve(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[tuple[str, tuple[Any, ...]]] = []

    def fake_fetch_one(sql: str, params: Sequence[Any] = ()) -> dict[str, Any] | None:
        if "FROM progression_palier WHERE Id" in sql:
            return {"seance_id": 5}
        if "FROM checklist WHERE seance_id" in sql:
            return {"id": 3}
        return None

    def fake_fetch_all(sql: str, params: Sequence[Any] = ()) -> list[dict[str, Any]]:
        return [{"id": 10}, {"id": 11}]

    def fake_execute(sql: str, params: Sequence[Any] = (), *, tx: Any = None) -> int:
        calls.append((sql, tuple(params)))
        return 1

    monkeypatch.setattr(m, "transaction", lambda: _FakeTx())
    monkeypatch.setattr(m, "fetch_one", fake_fetch_one)
    monkeypatch.setattr(m, "fetch_all", fake_fetch_all)
    monkeypatch.setattr(m, "execute", fake_execute)

    res = m.enregistrer_coches_prof(1, {10})

    assert res == {"items": 2, "coches": 1}
    paires = {(c[1][0], c[1][1]) for c in calls}
    assert paires == {(1, 10), (0, 11)}  # CocheProfesseur = 1 pour 10, 0 pour 11
    assert all("ON DUPLICATE KEY UPDATE CocheProfesseur = VALUES(CocheProfesseur)" in c[0] for c in calls)
    assert all("CocheEleve = VALUES" not in c[0] for c in calls)  # jamais le cochage élève
