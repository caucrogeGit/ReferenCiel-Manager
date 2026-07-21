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
    assert m._niveau_agrege(["NIVEAU_3", "NIVEAU_3"]) == "NIVEAU_3"
    assert m._niveau_agrege(["NIVEAU_1"]) == "NIVEAU_1"
    assert m._niveau_agrege(["NIVEAU_4", "NIVEAU_3"]) == "NIVEAU_3"  # (3+2)/2 = 2.5 -> 2
    assert m._niveau_agrege([]) == "non_evalue"
    assert m._niveau_agrege(["NON_OBSERVE"]) == "non_evalue"  # hors échelle -> ignoré


def test_agreger_synthese_groupe_par_competence(monkeypatch: pytest.MonkeyPatch) -> None:
    lignes = [
        {"competence_id": 1, "competence_code": "C01", "competence_intitule": "Analyser",
         "critere_code": "cr1", "critere_libelle": "…", "niveau": "NIVEAU_3"},
        {"competence_id": 1, "competence_code": "C01", "competence_intitule": "Analyser",
         "critere_code": "cr2", "critere_libelle": "…", "niveau": "NIVEAU_4"},
        {"competence_id": 2, "competence_code": "C03", "competence_intitule": "Câbler",
         "critere_code": "cr3", "critere_libelle": "…", "niveau": "NIVEAU_1"},
    ]

    def fake_fetch_all(sql: str, params: Sequence[Any] = ()) -> list[dict[str, Any]]:
        return lignes

    monkeypatch.setattr(m, "fetch_all", fake_fetch_all)
    synthese = m.agreger_synthese(10)

    assert len(synthese) == 2
    assert synthese[0]["competence_code"] == "C01"
    assert len(synthese[0]["criteres"]) == 2
    assert synthese[0]["niveau_agrege"] == "NIVEAU_3"  # (2+3)/2 = 2.5 -> 2
    assert synthese[1]["competence_code"] == "C03"
    assert synthese[1]["niveau_agrege"] == "NIVEAU_1"


def test_synthese_arretee_retient_ou_ajuste(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_agreger(pid: int) -> list[dict[str, Any]]:
        return [
            {"competence_id": 5, "competence_code": "C01", "niveau_agrege": "NIVEAU_3", "criteres": []},
            {"competence_id": 6, "competence_code": "C03", "niveau_agrege": "NIVEAU_2", "criteres": []},
        ]

    monkeypatch.setattr(m, "agreger_synthese", fake_agreger)
    # 5 : le prof ajuste vers le haut ; 6 : pas d'arbitrage → la suggestion est retenue.
    synth = m.synthese_arretee(10, {5: "NIVEAU_4"})

    assert synth[0]["niveau_suggere"] == "NIVEAU_3" and synth[0]["niveau_arrete"] == "NIVEAU_4"
    assert synth[1]["niveau_suggere"] == "NIVEAU_2" and synth[1]["niveau_arrete"] == "NIVEAU_2"
    assert "niveau_agrege" not in synth[0]  # remplacé par suggéré/arrêté


def test_synthese_arretee_ignore_un_niveau_invalide(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        m, "agreger_synthese",
        lambda pid: [{"competence_id": 5, "competence_code": "C01", "niveau_agrege": "NIVEAU_3", "criteres": []}],
    )
    synth = m.synthese_arretee(10, {5: "n_importe_quoi"})
    assert synth[0]["niveau_arrete"] == "NIVEAU_3"  # repli sur la suggestion


def test_creer_bilan_fige_la_synthese_et_deduit_l_eleve(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, Any] = {}

    def fake_fetch_one(sql: str, params: Sequence[Any] = ()) -> dict[str, Any] | None:
        return {"eleve_id": 7}

    def fake_agreger(pid: int) -> list[dict[str, Any]]:
        return [{"competence_id": 5, "competence_code": "C01", "niveau_agrege": "NIVEAU_3", "criteres": []}]

    def fake_insert(sql: str, params: Sequence[Any] = ()) -> int:
        captured["sql"] = sql
        captured["params"] = tuple(params)
        return 99

    monkeypatch.setattr(m, "fetch_one", fake_fetch_one)
    monkeypatch.setattr(m, "agreger_synthese", fake_agreger)
    monkeypatch.setattr(m, "insert", fake_insert)

    bilan_id = m.creer_bilan(
        progression_sequence_id=10, professeur_id=3, appreciation="Bon travail",
        statut="brouillon", niveaux_arretes={5: "NIVEAU_4"},
    )

    assert bilan_id == 99
    assert "INSERT INTO bilan_eleve" in captured["sql"]
    # eleve_id déduit (7), professeur (3), progression (10) transmis
    assert 7 in captured["params"] and 3 in captured["params"] and 10 in captured["params"]
    # la synthèse figée retient l'arbitrage du professeur
    synth = next(p for p in captured["params"] if isinstance(p, str) and "C01" in p)
    fige = json.loads(synth)
    assert fige[0]["competence_code"] == "C01"
    assert fige[0]["niveau_arrete"] == "NIVEAU_4" and fige[0]["niveau_suggere"] == "NIVEAU_3"


def test_creer_bilan_progression_absente_renvoie_none(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(m, "fetch_one", lambda sql, params=(): None)
    assert (
        m.creer_bilan(
            progression_sequence_id=999, professeur_id=3, appreciation="x",
            statut="brouillon", niveaux_arretes={},
        )
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
