"""Tests de la notation par critères (évaluation prof) sans backend BDD.

`core.database` mocké : on vérifie le find-or-create de l'`evaluation_activite`
(professeur de l'affectation), l'upsert des niveaux de critères, le filtrage des
niveaux hors échelle, et l'absence d'activité → None. CI-safe (ADR-006).
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


def _install(monkeypatch: pytest.MonkeyPatch, *, ctx: dict[str, Any] | None, eval_existante: dict[str, Any] | None) -> dict[str, list[Any]]:
    cap: dict[str, list[Any]] = {"insert": [], "execute": []}

    def fake_fetch_one(sql: str, params: Sequence[Any] = ()) -> dict[str, Any] | None:
        if "FROM progression_palier pp" in sql:
            return ctx
        if "FROM evaluation_activite" in sql:
            return eval_existante
        return None

    def fake_insert(sql: str, params: Sequence[Any] = (), *, tx: Any = None) -> int:
        cap["insert"].append((sql, tuple(params)))
        return 50

    def fake_execute(sql: str, params: Sequence[Any] = (), *, tx: Any = None) -> int:
        cap["execute"].append((sql, tuple(params)))
        return 1

    monkeypatch.setattr(m, "transaction", lambda: _FakeTx())
    monkeypatch.setattr(m, "fetch_one", fake_fetch_one)
    monkeypatch.setattr(m, "insert", fake_insert)
    monkeypatch.setattr(m, "execute", fake_execute)
    return cap


_CTX = {"pp_id": 1, "progression_id": 1, "palier_titre": "P", "nom": "D", "prenom": "J", "professeur_id": 2, "activite_id": 9}


def test_cree_l_evaluation_et_upsert_les_niveaux_valides(monkeypatch: pytest.MonkeyPatch) -> None:
    cap = _install(monkeypatch, ctx=_CTX, eval_existante=None)

    res = m.enregistrer_notation(1, {7: "atteint", 8: "n_importe_quoi", 9: "depasse"})

    assert res == {"notes": 2}  # le niveau hors échelle (8) est ignoré
    # evaluation_activite créée avec le professeur de l'affectation
    assert len(cap["insert"]) == 1
    assert cap["insert"][0][1] == (1, 9, 2)  # progression_palier, activite, professeur
    # upsert d'un evaluation_critere par critère valide
    paires = {(c[1][0], c[1][2]) for c in cap["execute"]}  # (niveau, critere_id)
    assert paires == {("atteint", 7), ("depasse", 9)}
    assert all("ON DUPLICATE KEY UPDATE Niveau = VALUES(Niveau)" in c[0] for c in cap["execute"])


def test_reutilise_l_evaluation_existante(monkeypatch: pytest.MonkeyPatch) -> None:
    cap = _install(monkeypatch, ctx=_CTX, eval_existante={"id": 50})
    m.enregistrer_notation(1, {7: "atteint"})
    assert cap["insert"] == []  # pas de nouvelle evaluation_activite
    assert cap["execute"][0][1] == ("atteint", 50, 7)


def test_palier_sans_activite_renvoie_none(monkeypatch: pytest.MonkeyPatch) -> None:
    cap = _install(monkeypatch, ctx={**_CTX, "activite_id": None}, eval_existante=None)
    assert m.enregistrer_notation(1, {7: "atteint"}) is None
    assert cap["insert"] == [] and cap["execute"] == []
