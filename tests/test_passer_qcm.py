"""Tests de la saisie élève « passer un QCM » sans backend BDD.

`core.database` est mocké : on vérifie le **scoring côté serveur** (lettre du choix
vs bonne réponse), la mise à jour du **statut** de la séance (100 % → validé, sinon en
cours), et le **contrôle d'appartenance** (séance d'autrui → None). CI-safe (ADR-006).
"""
from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import pytest

from mvc.models import passer_qcm_model as m


class _FakeTx:
    def __enter__(self) -> "_FakeTx":
        return self

    def __exit__(self, *a: object) -> bool:
        return False


def _install(
    monkeypatch: pytest.MonkeyPatch,
    *,
    seance: dict[str, Any] | None,
    lettres_choix: dict[int, str],
    bonnes: dict[int, str],
) -> dict[str, Any]:
    """Installe les mocks DB et retourne un dict capturant insert/execute."""
    cap: dict[str, Any] = {"execute": [], "insert": []}

    def fake_fetch_one(sql: str, params: Sequence[Any] = ()) -> dict[str, Any] | None:
        if "FROM progression_seance pp" in sql:
            return seance
        if "FROM qcm WHERE seance_id" in sql:
            return {"id": 9}
        if "FROM choix_qcm WHERE Id" in sql:
            choix_id = int(params[0])
            return {"lettre": lettres_choix[choix_id]}
        if "MAX(NumeroTentative)" in sql:
            return {"n": 0}
        return None

    def fake_fetch_all(sql: str, params: Sequence[Any] = ()) -> list[dict[str, Any]]:
        if "BonneReponse" in sql:
            return [{"id": qid, "bonne": bonne} for qid, bonne in bonnes.items()]
        return []

    def fake_insert(sql: str, params: Sequence[Any] = (), *, tx: Any = None) -> int:
        cap["insert"].append((sql, tuple(params)))
        return 77

    def fake_execute(sql: str, params: Sequence[Any] = (), *, tx: Any = None) -> int:
        cap["execute"].append((sql, tuple(params)))
        return 1

    monkeypatch.setattr(m, "transaction", lambda: _FakeTx())
    monkeypatch.setattr(m, "fetch_one", fake_fetch_one)
    monkeypatch.setattr(m, "fetch_all", fake_fetch_all)
    monkeypatch.setattr(m, "insert", fake_insert)
    monkeypatch.setattr(m, "execute", fake_execute)
    return cap


_SEANCE = {"progression_seance_id": 1, "seance_id": 5, "seance_titre": "P"}


def test_score_partiel_ne_valide_pas_le_seance(monkeypatch: pytest.MonkeyPatch) -> None:
    # q1 bonne A (choix 101 = A → juste) ; q2 bonne B (choix 202 = C → faux)
    cap = _install(
        monkeypatch, seance=_SEANCE,
        lettres_choix={101: "A", 202: "C"}, bonnes={1: "A", 2: "B"},
    )
    res = m.enregistrer_tentative(1, 42, {1: 101, 2: 202})

    assert res == {"score": 50, "total": 2, "validee": False, "numero": 1}
    # tentative : score 50, non validée
    assert cap["insert"][0][1] == (1, 50, 0, 1)
    # deux réponses figées + une mise à jour de statut vers en_cours
    maj = [c for c in cap["execute"] if "UPDATE progression_seance" in c[0]][0]
    assert "en_cours" in maj[1]


def test_tout_juste_valide_le_seance(monkeypatch: pytest.MonkeyPatch) -> None:
    cap = _install(
        monkeypatch, seance=_SEANCE,
        lettres_choix={101: "A", 201: "B"}, bonnes={1: "A", 2: "B"},
    )
    res = m.enregistrer_tentative(1, 42, {1: 101, 2: 201})

    assert res is not None and res["validee"] is True and res["score"] == 100
    assert cap["insert"][0][1] == (1, 100, 1, 1)  # Validee = 1
    maj = [c for c in cap["execute"] if "UPDATE progression_seance" in c[0]][0]
    assert "valide" in maj[1]
    # garde anti-régression : ne met à jour que si la séance n'est pas déjà validé
    assert "Statut <> ?" in maj[0]


def test_seance_d_autrui_renvoie_none(monkeypatch: pytest.MonkeyPatch) -> None:
    cap = _install(monkeypatch, seance=None, lettres_choix={}, bonnes={})
    assert m.enregistrer_tentative(1, 42, {1: 101}) is None
    assert cap["insert"] == [] and cap["execute"] == []  # aucune écriture
