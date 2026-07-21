"""Tests de la feuille de positionnement (notation par critères, ADR-032/033) sans backend BDD.

`core.database` mocké : on vérifie le find-or-create de l'observation
(`evaluation_activite`, professeur du compte connecté — ADR-022), l'upsert
explicite des niveaux CIEL de critères, le fait qu'un niveau « non observé » (ou
hors échelle) **efface** la ligne, l'enregistrement de la production/aide/appréciation,
et l'absence de professeur / de progression_seance → None. CI-safe (ADR-006).
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
    ctx: dict[str, Any] | None,
    obs: dict[str, Any] | None,
    prof_fiche: dict[str, Any] | None = None,
    critere_existant: dict[str, Any] | None = None,
) -> dict[str, list[Any]]:
    cap: dict[str, list[Any]] = {"insert": [], "execute": []}

    def fake_fetch_one(sql: str, params: Sequence[Any] = (), *, tx: Any = None) -> dict[str, Any] | None:
        if "FROM progression_seance pp" in sql:
            return ctx
        if "FROM professeur WHERE UserId" in sql:
            return prof_fiche
        if "FROM evaluation_critere" in sql:
            return critere_existant
        if "FROM evaluation_activite" in sql:
            return obs
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


_CTX = {
    "pp_id": 1, "progression_id": 1, "statut": "en_cours", "seance_id": 5,
    "seance_titre": "P", "nom": "D", "prenom": "J",
}


def _inserts(cap: dict[str, list[Any]], table: str) -> list[tuple[Any, ...]]:
    return [params for sql, params in cap["insert"] if f"INSERT INTO {table}" in sql]


def test_cree_l_observation_et_positionne_les_criteres(monkeypatch: pytest.MonkeyPatch) -> None:
    cap = _install(monkeypatch, ctx=_CTX, obs=None, prof_fiche={"id": 2})

    res = m.enregistrer_notation(
        1, {7: "NIVEAU_3", 8: "n_importe_quoi", 9: "NIVEAU_4"}, user_id=99,
        production="p", aide="a", appreciation="ap",
    )

    # 8 (hors grille CIEL) est traité comme « non observé » → pas compté, ligne effacée.
    assert res == {"notes": 2}
    # Observation créée avec le professeur du compte connecté + production/aide/appréciation.
    obs_ins = _inserts(cap, "evaluation_activite")
    assert obs_ins == [(1, 2, "ap", "p", "a")]  # progression_seance, professeur, appréciation, production, aide
    # Un evaluation_critere inséré par critère positionné (obs neuve → pas de ligne existante).
    paires = {(p[0], p[2]) for p in _inserts(cap, "evaluation_critere")}  # (niveau, critere_id)
    assert paires == {("NIVEAU_3", 7), ("NIVEAU_4", 9)}
    # Le critère hors échelle (8) est effacé.
    assert any("DELETE FROM evaluation_critere" in sql and params[1] == 8 for sql, params in cap["execute"])


def test_attribue_au_professeur_connecte(monkeypatch: pytest.MonkeyPatch) -> None:
    cap = _install(monkeypatch, ctx=_CTX, obs=None, prof_fiche={"id": 42})
    m.enregistrer_notation(1, {7: "NIVEAU_3"}, user_id=99)
    assert _inserts(cap, "evaluation_activite")[0][1] == 42  # professeur du compte


def test_sans_professeur_connecte_renvoie_none(monkeypatch: pytest.MonkeyPatch) -> None:
    cap = _install(monkeypatch, ctx=_CTX, obs=None, prof_fiche=None)
    assert m.enregistrer_notation(1, {7: "NIVEAU_3"}, user_id=99) is None
    assert cap["insert"] == [] and cap["execute"] == []


def test_reutilise_l_observation_existante(monkeypatch: pytest.MonkeyPatch) -> None:
    cap = _install(monkeypatch, ctx=_CTX, obs={"id": 50}, prof_fiche={"id": 2}, critere_existant=None)
    m.enregistrer_notation(1, {7: "NIVEAU_3"}, user_id=99)
    assert _inserts(cap, "evaluation_activite") == []  # pas de nouvelle observation
    assert any("UPDATE evaluation_activite" in sql for sql, _ in cap["execute"])
    assert _inserts(cap, "evaluation_critere")[0] == ("NIVEAU_3", 50, 7)


def test_met_a_jour_un_critere_deja_positionne(monkeypatch: pytest.MonkeyPatch) -> None:
    cap = _install(monkeypatch, ctx=_CTX, obs={"id": 50}, prof_fiche={"id": 2}, critere_existant={"id": 77})
    m.enregistrer_notation(1, {7: "NIVEAU_4"}, user_id=99)
    assert _inserts(cap, "evaluation_critere") == []  # pas d'insert : mise à jour
    assert any("UPDATE evaluation_critere" in sql and params == ("NIVEAU_4", 77)
               for sql, params in cap["execute"])


def test_non_observe_efface_la_ligne(monkeypatch: pytest.MonkeyPatch) -> None:
    cap = _install(monkeypatch, ctx=_CTX, obs={"id": 50}, prof_fiche={"id": 2})
    res = m.enregistrer_notation(1, {7: "NON_OBSERVE"}, user_id=99)
    assert res == {"notes": 0}
    assert _inserts(cap, "evaluation_critere") == []
    assert any("DELETE FROM evaluation_critere" in sql and params == (50, 7)
               for sql, params in cap["execute"])


def test_progression_seance_absente_renvoie_none(monkeypatch: pytest.MonkeyPatch) -> None:
    cap = _install(monkeypatch, ctx=None, obs=None, prof_fiche={"id": 2})
    assert m.enregistrer_notation(1, {7: "NIVEAU_3"}, user_id=99) is None
    assert cap["insert"] == [] and cap["execute"] == []
