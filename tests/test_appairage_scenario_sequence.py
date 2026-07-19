# pyright: strict
"""Appairage 1-1 Scénario ↔ Séquence à la création (ADR-029).

`core.database` est mocké : on vérifie que chaque sens de création émet bien les
trois écritures de la paire (scénario, séquence, lien), sans base réelle — donc
exécutable en CI.
"""
from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import pytest

from mvc.models import scenario_editeur_model as m


class _Rec:
    """Enregistre les écritures et simule des Id auto-incrémentés."""

    def __init__(self) -> None:
        self._n = 0
        self.inserts: list[tuple[str, tuple[Any, ...]]] = []
        self.execs: list[tuple[str, tuple[Any, ...]]] = []

    def insert(self, sql: str, params: Sequence[Any] = (), *, tx: object = None) -> int:
        self._n += 1
        self.inserts.append((sql, tuple(params)))
        return self._n

    def execute(self, sql: str, params: Sequence[Any] = (), *, tx: object = None) -> int:
        self.execs.append((sql, tuple(params)))
        return 0


class _Tx:
    def __enter__(self) -> object:
        return object()

    def __exit__(self, *_: object) -> bool:
        return False


def _patch(monkeypatch: pytest.MonkeyPatch, rec: _Rec) -> None:
    monkeypatch.setattr(m, "insert", rec.insert)
    monkeypatch.setattr(m, "execute", rec.execute)
    monkeypatch.setattr(m, "transaction", lambda: _Tx())


def test_scenario_first_cree_la_paire(monkeypatch: pytest.MonkeyPatch) -> None:
    """creer_scenario écrit le scénario, sa séquence jumelle et le lien."""
    rec = _Rec()
    _patch(monkeypatch, rec)

    scenario_id = m.creer_scenario("Mon titre", None)

    assert scenario_id == 1  # 1er insert = scénario
    assert "INSERT INTO scenario " in rec.inserts[0][0]
    assert rec.inserts[0][1] == ("Mon titre", None)
    assert "INSERT INTO sequence " in rec.inserts[1][0]
    # (identifiant dérivé, titre partagé, niveau vide)
    assert rec.inserts[1][1] == ("mon-titre", "Mon titre", None)
    assert "INSERT INTO scenario_sequence" in rec.execs[0][0]
    assert rec.execs[0][1] == (1, 2)  # (scenario_id, sequence_id)


def test_sequence_first_cree_la_paire(monkeypatch: pytest.MonkeyPatch) -> None:
    """creer_sequence_et_scenario écrit la séquence, son scénario jumeau et le lien."""
    rec = _Rec()
    _patch(monkeypatch, rec)

    sequence_id = m.creer_sequence_et_scenario("SEQ-1", "Titre B", 5)

    assert sequence_id == 1  # 1er insert = séquence
    assert "INSERT INTO sequence " in rec.inserts[0][0]
    assert rec.inserts[0][1] == ("SEQ-1", "Titre B", 5)
    assert "INSERT INTO scenario " in rec.inserts[1][0]
    # titre partagé, scénario hors référentiel (referentiel_id None)
    assert rec.inserts[1][1] == ("Titre B", None)
    assert rec.execs[0][1] == (2, 1)  # (scenario_id, sequence_id)


def test_backfill_cree_la_jumelle(monkeypatch: pytest.MonkeyPatch) -> None:
    """creer_sequence_jumelle relie une séquence neuve à un scénario existant."""
    rec = _Rec()
    _patch(monkeypatch, rec)

    sequence_id = m.creer_sequence_jumelle(42, "Test")

    assert sequence_id == 1
    assert "INSERT INTO sequence " in rec.inserts[0][0]
    assert rec.inserts[0][1] == ("test", "Test", None)
    assert rec.execs[0][1] == (42, 1)  # (scenario_id existant, sequence_id neuve)
