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


def _no_row(sql: str, params: Sequence[Any] = (), *, tx: object = None) -> None:
    """fetch_one qui ne trouve rien (identifiant libre : pas de suffixe)."""
    return None


def _patch(monkeypatch: pytest.MonkeyPatch, rec: _Rec) -> None:
    monkeypatch.setattr(m, "insert", rec.insert)
    monkeypatch.setattr(m, "execute", rec.execute)
    monkeypatch.setattr(m, "transaction", lambda: _Tx())
    # _identifiant_sequence_unique interroge fetch_one : aucune collision ici.
    monkeypatch.setattr(m, "fetch_one", _no_row)


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

    sequence_id = m.creer_sequence_et_scenario("Titre B", 5)

    assert sequence_id == 1  # 1er insert = séquence
    assert "INSERT INTO sequence " in rec.inserts[0][0]
    # identifiant dérivé du titre, niveau vide à la création (réglé ensuite)
    assert rec.inserts[0][1] == ("titre-b", "Titre B", None)
    assert "INSERT INTO scenario " in rec.inserts[1][0]
    # titre partagé, référentiel (5) posé sur le scénario jumeau
    assert rec.inserts[1][1] == ("Titre B", 5)
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


def _statuts(sc: "str | None", sq: "str | None") -> object:
    def _f(sql: str, params: Sequence[Any] = (), *, tx: object = None) -> "dict[str, Any] | None":
        return {"statut_scenario": sc, "statut_sequence": sq}
    return _f


def test_identifiant_sequence_suffixe_en_cas_de_collision(monkeypatch: pytest.MonkeyPatch) -> None:
    """L'identifiant de séquence est suffixé si le slug est déjà pris (uq_sequence_identifiant)."""
    existants: set[str] = {"test"}

    def _fo(sql: str, params: Sequence[Any] = (), *, tx: object = None) -> "dict[str, Any] | None":
        return {"x": 1} if params and params[0] in existants else None

    monkeypatch.setattr(m, "fetch_one", _fo)
    assert m._identifiant_sequence_unique("test") == "test-2"  # pyright: ignore[reportPrivateUsage]
    existants.add("test-2")
    assert m._identifiant_sequence_unique("test") == "test-3"  # pyright: ignore[reportPrivateUsage]
    assert m._identifiant_sequence_unique("libre") == "libre"  # pyright: ignore[reportPrivateUsage]


def test_verrou_referentiel_paire_finalisee(monkeypatch: pytest.MonkeyPatch) -> None:
    """Le référentiel est verrouillé dès qu'un côté est finalisé (ou utilisé)."""
    monkeypatch.setattr(m, "fetch_one", _statuts("brouillon", "brouillon"))
    assert m.paire_est_finalisee(1) is False
    monkeypatch.setattr(m, "fetch_one", _statuts("finalise", "brouillon"))
    assert m.paire_est_finalisee(1) is True  # scénario finalisé
    monkeypatch.setattr(m, "fetch_one", _statuts("brouillon", "finalise"))
    assert m.paire_est_finalisee(1) is True  # séquence finalisée
    monkeypatch.setattr(m, "fetch_one", _statuts("utilise", None))
    assert m.paire_est_finalisee(1) is True  # utilisé verrouille aussi
