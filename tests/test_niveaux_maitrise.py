# pyright: strict
"""Niveaux de maîtrise CIEL (ADR-032/033) : suggestion et descripteurs."""
from __future__ import annotations

from mvc.services.niveaux_maitrise import suggerer_niveau, niveau, NIVEAUX_POSITIONNABLES


def test_suggestion_reproduit_exemple_4_observables() -> None:
    assert suggerer_niveau(0, 4) == "NIVEAU_1"
    assert suggerer_niveau(1, 4) == "NIVEAU_2"
    assert suggerer_niveau(2, 4) == "NIVEAU_3"
    assert suggerer_niveau(3, 4) == "NIVEAU_3"
    assert suggerer_niveau(4, 4) == "NIVEAU_4"


def test_suggestion_nombre_reel_d_indicateurs() -> None:
    # Seuils non figés : calcul sur le nombre réel.
    assert suggerer_niveau(0, 0) == "NON_OBSERVE"
    assert suggerer_niveau(1, 1) == "NIVEAU_4"
    assert suggerer_niveau(1, 3) == "NIVEAU_2"  # 33 % < 50 %
    assert suggerer_niveau(2, 3) == "NIVEAU_3"  # 66 % ≥ 50 %


def test_non_observe_distinct_du_rouge() -> None:
    assert niveau(None)["code"] == "NON_OBSERVE"
    assert niveau(None)["couleur"] == "gris"
    assert niveau("NON_OBSERVE")["niveau"] is None
    assert niveau("NIVEAU_1")["couleur"] == "rouge"
    assert niveau("NIVEAU_1")["libelle"] == "Non réalisé"


def test_quatre_niveaux_positionnables() -> None:
    assert [n["niveau"] for n in NIVEAUX_POSITIONNABLES] == [1, 2, 3, 4]
