# pyright: strict
"""Regroupement des listes de cartes en sections (helpers.groupes)."""
from __future__ import annotations

from mvc.helpers.groupes import grouper, libelle_referentiel


def test_grouper_decoupe_en_sections_consecutives_sans_retrier() -> None:
    rows = [
        {"ref": "A", "id": 1},
        {"ref": "A", "id": 2},
        {"ref": "B", "id": 3},
        {"ref": None, "id": 4},
    ]
    groupes = grouper(rows, lambda r: r["ref"], "Hors référentiel")
    assert [g["label"] for g in groupes] == ["A", "B", "Hors référentiel"]
    assert [c["id"] for c in groupes[0]["cartes"]] == [1, 2]
    assert [c["id"] for c in groupes[2]["cartes"]] == [4]


def test_grouper_liste_vide() -> None:
    assert grouper([], lambda r: None, "x") == []


def test_libelle_referentiel_formation_et_identifiant() -> None:
    assert libelle_referentiel(
        {"referentiel_identifiant": "2tne-ciel", "formation_intitule": "Métiers TNE"}
    ) == "Métiers TNE · 2tne-ciel"
    assert libelle_referentiel({"referentiel_identifiant": "2tne-ciel"}) == "2tne-ciel"
    assert libelle_referentiel({"referentiel_identifiant": None}) is None
