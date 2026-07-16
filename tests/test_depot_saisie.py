"""Tests de la saisie élève « déposer un fichier » sans backend BDD.

`core.database` mocké : on vérifie l'insertion du dépôt (chemin du fichier, seance,
activité) et le contrôle d'appartenance (séance d'autrui → None, aucune écriture).
CI-safe (ADR-006).
"""
from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import pytest

from mvc.models import depot_saisie_model as m


def _install(monkeypatch: pytest.MonkeyPatch, *, seance: dict[str, Any] | None, activite: dict[str, Any] | None) -> list[tuple[str, tuple[Any, ...]]]:
    inserts: list[tuple[str, tuple[Any, ...]]] = []

    def fake_fetch_one(sql: str, params: Sequence[Any] = ()) -> dict[str, Any] | None:
        if "FROM progression_palier pp" in sql:
            return seance
        if "FROM activite WHERE seance_id" in sql:
            return activite
        return None

    def fake_insert(sql: str, params: Sequence[Any] = (), *, tx: Any = None) -> int:
        inserts.append((sql, tuple(params)))
        return 88

    monkeypatch.setattr(m, "fetch_one", fake_fetch_one)
    monkeypatch.setattr(m, "insert", fake_insert)
    return inserts


def test_enregistre_le_depot_avec_chemin_seance_et_activite(monkeypatch: pytest.MonkeyPatch) -> None:
    inserts = _install(
        monkeypatch,
        seance={"progression_palier_id": 1, "seance_id": 5, "seance_titre": "P"},
        activite={"id": 9, "consigne": None},
    )

    res = m.enregistrer_depot(1, 42, "depots/abc.pdf")

    assert res == {"depot_id": 88, "activite_id": 9}
    assert len(inserts) == 1
    sql, params = inserts[0]
    assert "INSERT INTO depot_eleve" in sql
    assert params == ("depots/abc.pdf", 1, 9)  # fichier, progression_palier_id, activite_id


def test_seance_d_autrui_renvoie_none(monkeypatch: pytest.MonkeyPatch) -> None:
    inserts = _install(monkeypatch, seance=None, activite=None)
    assert m.enregistrer_depot(1, 42, "depots/abc.pdf") is None
    assert inserts == []  # aucune écriture


def test_seance_sans_activite_renvoie_none(monkeypatch: pytest.MonkeyPatch) -> None:
    inserts = _install(
        monkeypatch,
        seance={"progression_palier_id": 1, "seance_id": 5, "seance_titre": "P"},
        activite=None,
    )
    assert m.enregistrer_depot(1, 42, "depots/abc.pdf") is None
    assert inserts == []
