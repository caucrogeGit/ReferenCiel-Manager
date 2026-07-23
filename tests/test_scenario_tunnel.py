# pyright: strict
"""Tests de la logique pure du tunnel d'édition de scénario (ADR-019, ADR-021).

Extraite du contrôleur dans `mvc.services.scenario_tunnel`, elle se teste sans
HTTP : bornage d'étape, complétion dérivée des données, analyse des identifiants
soumis, navigation et ouverture du maître-détail sur la sélection existante.
"""
from __future__ import annotations

from typing import Any

from mvc.services.scenario_tunnel import (
    ETAPES,
    borner_etape,
    navigation,
    ouvrir_sur_selection,
    parse_id,
    parse_ids,
    selection_courante,
    slug,
    steps,
)

# ── parse_id / parse_ids ────────────────────────────────────────────────────


def test_parse_id_valeurs_valides_et_forgees() -> None:
    assert parse_id("12") == 12
    assert parse_id(7) == 7
    assert parse_id("abc") is None
    assert parse_id(None) is None
    assert parse_id("") is None


def test_parse_ids_dedoublonne_et_filtre() -> None:
    assert parse_ids(["3", "1", "3", "abc", "-2", "0"]) == [3, 1]
    assert parse_ids("5") == [5]  # valeur seule (champ non multiple)
    assert parse_ids(None) == []
    assert parse_ids([]) == []


# ── Étapes et navigation ────────────────────────────────────────────────────


def test_borner_etape() -> None:
    assert borner_etape("liaison") == "liaison"
    assert borner_etape("inconnue") == "titre"
    assert borner_etape("") == "titre"


def test_navigation_bornes_du_tunnel() -> None:
    premiere = navigation(ETAPES[0])
    assert premiere["position"] == 1
    assert premiere["prev"] is None
    assert premiere["next"] == {"key": "contexte", "label": "Contexte"}

    derniere = navigation(ETAPES[-1])
    assert derniere["position"] == len(ETAPES)
    assert derniere["next"] is None
    assert derniere["prev"] == {"key": "liaison", "label": "Liaison référentiel"}


# ── Complétion dérivée (steps) ──────────────────────────────────────────────


def _scenario_complet() -> dict[str, Any]:
    return {
        "Titre": "Réseau local",
        "referentiel_id": 1,  # adossé à un référentiel (cas normal)
        "DescriptionContexte": "x",
        "Problematique": "x",
        "MaterielsLogiciels": "x",
        "LiensAssocies": "x",
        "EspacesFormation": "x",
    }


def test_steps_scenario_complet() -> None:
    barre = steps(_scenario_complet(), activite_ids=[1], critere_ids=[2])
    assert [s["done"] for s in barre] == [True, True, True, True]


def test_steps_contexte_incomplet_et_liaison_vide() -> None:
    scenario = _scenario_complet()
    scenario["DescriptionContexte"] = ""  # seul champ obligatoire du contexte
    barre = steps(scenario, activite_ids=[], critere_ids=[2])
    done = {s["key"]: s["done"] for s in barre}
    assert done["contexte"] is False
    assert done["liaison"] is False  # il faut activité ET critère
    assert done["gestion"] is True  # outillage (ADR-038) : ne bloque jamais


def test_steps_contexte_complet_avec_seule_la_description() -> None:
    # Seule la description est obligatoire : les autres champs cpro vides
    # (problématique, matériels, liens, espaces) ne bloquent plus l'étape.
    scenario = _scenario_complet()
    for champ in ("Problematique", "MaterielsLogiciels", "LiensAssocies", "EspacesFormation"):
        scenario[champ] = ""
    contexte = next(s for s in steps(scenario, activite_ids=[1], critere_ids=[2]) if s["key"] == "contexte")
    assert contexte["done"] is True


def test_steps_hors_referentiel_liaison_grisee() -> None:
    # Sans référentiel (ADR-027) : l'étape Liaison est inactive et ne bloque pas.
    scenario = _scenario_complet()
    scenario["referentiel_id"] = None
    liaison = next(s for s in steps(scenario, activite_ids=[], critere_ids=[]) if s["key"] == "liaison")
    assert liaison["inactif"] is True
    assert liaison["done"] is True


# ── Sélection du maître-détail ──────────────────────────────────────────────


def test_selection_courante_sans_arbre() -> None:
    assert selection_courante(None, "1", "2") == (None, None)


def test_selection_courante_avec_arbre() -> None:
    arbre: dict[str, Any] = {"poles": [], "competences": []}
    assert selection_courante(arbre, "1", "") == (1, None)


def test_ouvrir_sur_selection_ouvre_le_premier_item_coche() -> None:
    arbre: dict[str, Any] = {
        "poles": [
            {"Id": 1, "activites": [{"Id": 10}]},
            {"Id": 2, "activites": [{"Id": 20}]},
        ],
        "competences": [
            {"Id": 3, "criteres": [{"Id": 30}]},
            {"Id": 4, "criteres": [{"Id": 40}]},
        ],
    }
    # Rien coché : rien d'ouvert (scénario vierge).
    assert ouvrir_sur_selection(arbre, None, None, [], []) == (None, None)
    # Le pôle/la compétence du premier item coché s'ouvrent.
    assert ouvrir_sur_selection(arbre, None, None, [20], [40]) == (2, 4)
    # Un choix explicite n'est jamais écrasé.
    assert ouvrir_sur_selection(arbre, 1, 3, [20], [40]) == (1, 3)


# ── Slug de fichier PDF ─────────────────────────────────────────────────────


def test_slug_nom_de_fichier_sur() -> None:
    assert slug("Réseau local : phase 1 !") == "réseau-local-phase-1"
    assert slug("///") == "scenario"
    assert len(slug("x" * 200)) == 60
