"""Tests du bilan élève (ticket 21) sans backend BDD.

`core.database` est mocké : on vérifie l'agrégation par compétence (niveau ordinal),
le **figement** de la synthèse en JSON à la création, la déduction de l'`eleve_id`
depuis la progression, et la désérialisation à la lecture. CI-safe (ADR-006).
"""
from __future__ import annotations

import json
from collections.abc import Sequence
from typing import Any

import pytest

from mvc.models import bilan_eleve_model as m


def test_niveau_agrege_moyenne_ordinale() -> None:
    assert m._niveau_agrege(["atteint", "atteint"]) == "atteint"
    assert m._niveau_agrege(["non_atteint"]) == "non_atteint"
    assert m._niveau_agrege(["depasse", "atteint"]) == "atteint"  # (3+2)/2 = 2.5 -> 2
    assert m._niveau_agrege([]) == "non_evalue"
    assert m._niveau_agrege(["inconnu"]) == "non_evalue"  # hors échelle -> ignoré


def test_agreger_synthese_groupe_par_competence(monkeypatch: pytest.MonkeyPatch) -> None:
    lignes = [
        {"competence_id": 1, "competence_code": "C01", "competence_intitule": "Analyser",
         "critere_code": "cr1", "critere_libelle": "…", "niveau": "atteint"},
        {"competence_id": 1, "competence_code": "C01", "competence_intitule": "Analyser",
         "critere_code": "cr2", "critere_libelle": "…", "niveau": "depasse"},
        {"competence_id": 2, "competence_code": "C03", "competence_intitule": "Câbler",
         "critere_code": "cr3", "critere_libelle": "…", "niveau": "non_atteint"},
    ]

    def fake_fetch_all(sql: str, params: Sequence[Any] = ()) -> list[dict[str, Any]]:
        return lignes

    monkeypatch.setattr(m, "fetch_all", fake_fetch_all)
    synthese = m.agreger_synthese(10)

    assert len(synthese) == 2
    assert synthese[0]["competence_code"] == "C01"
    assert len(synthese[0]["criteres"]) == 2
    assert synthese[0]["niveau_agrege"] == "atteint"  # (2+3)/2 = 2.5 -> 2
    assert synthese[1]["competence_code"] == "C03"
    assert synthese[1]["niveau_agrege"] == "non_atteint"


def test_creer_bilan_fige_la_synthese_et_deduit_l_eleve(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, Any] = {}

    def fake_fetch_one(sql: str, params: Sequence[Any] = ()) -> dict[str, Any] | None:
        return {"eleve_id": 7}

    def fake_agreger(pid: int) -> list[dict[str, Any]]:
        return [{"competence_code": "C01", "niveau_agrege": "atteint", "criteres": []}]

    def fake_insert(sql: str, params: Sequence[Any] = ()) -> int:
        captured["sql"] = sql
        captured["params"] = tuple(params)
        return 99

    monkeypatch.setattr(m, "fetch_one", fake_fetch_one)
    monkeypatch.setattr(m, "agreger_synthese", fake_agreger)
    monkeypatch.setattr(m, "insert", fake_insert)

    bilan_id = m.creer_bilan(
        progression_eleve_id=10, professeur_id=3, appreciation="Bon travail", statut="brouillon"
    )

    assert bilan_id == 99
    assert "INSERT INTO bilan_eleve" in captured["sql"]
    # eleve_id déduit (7), professeur (3), progression (10) transmis
    assert 7 in captured["params"] and 3 in captured["params"] and 10 in captured["params"]
    # la synthèse est figée sous forme de JSON sérialisé
    synth = next(p for p in captured["params"] if isinstance(p, str) and "C01" in p)
    assert json.loads(synth)[0]["competence_code"] == "C01"


def test_creer_bilan_progression_absente_renvoie_none(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(m, "fetch_one", lambda sql, params=(): None)
    assert (
        m.creer_bilan(progression_eleve_id=999, professeur_id=3, appreciation="x", statut="brouillon")
        is None
    )


def test_get_bilan_deserialise_la_synthese(monkeypatch: pytest.MonkeyPatch) -> None:
    row: dict[str, Any] = {
        "id": 1, "appreciation": "ok", "statut": "publie", "date_bilan": "2026-07-11",
        "synthese": json.dumps([{"competence_code": "C01"}]),
        "eleve_nom": "Dupont", "eleve_prenom": "Marie", "prof_nom": "Bernard", "prof_prenom": "Julie",
    }
    monkeypatch.setattr(m, "fetch_one", lambda sql, params=(): row)

    bilan = m.get_bilan(1)

    assert bilan is not None
    assert isinstance(bilan["synthese"], list)
    assert bilan["synthese"][0]["competence_code"] == "C01"
