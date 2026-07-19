# pyright: strict
"""Tests des exports Markdown et JSON d'un scénario.

Les formatters (`rendre_markdown`, `rendre_json`) sont **purs** : ils prennent le
dict assemblé par `scenario_pdf.assembler_scenario` et n'accèdent pas à la base.
On les exerce donc sur un dict de référence, sans backend.
"""
from __future__ import annotations

import json
from typing import Any

from mvc.services.scenario_export import rendre_json, rendre_markdown

_DATA: dict[str, Any] = {
    "scenario": {
        "Titre": "Créer un câble Ethernet",
        "Statut": "finalise",
        "Intention": "Câbler et tester un lien Ethernet.",
        "Objectifs": "Sertir et valider un câble droit T568B.",
        "CoIntervention": 1,
    },
    "referentiel": {"Identifiant": "2tne-ciel", "formation_intitule": "2TNE"},
    "co_auteurs": ["Marie Bernard"],
    "contexte": [
        {"libelle": "Description du contexte", "valeur": "Atelier réseau."},
        {"libelle": "Problématique", "valeur": "Relier deux postes."},
    ],
    "activites": [
        {
            "code": "A1", "intitule": "Câblage", "pole": "Réseaux",
            "competences": [
                {
                    "code": "C03", "intitule": "Câbler", "cc_codes": [],
                    "criteres": [
                        {"libelle": "Le câble est conforme", "savoir_etre": False,
                         "indicateurs": ["Continuité OK"]},
                        {"libelle": "Travail soigneux", "savoir_etre": True, "indicateurs": []},
                    ],
                },
            ],
        },
    ],
    "ressources": [
        {"NomOriginal": "schema.pdf", "MimeType": "application/pdf", "Taille": 1234},
    ],
}


# ── JSON ─────────────────────────────────────────────────────────────────────

def test_json_valide_et_structure() -> None:
    doc = json.loads(rendre_json(_DATA))
    assert doc["titre"] == "Créer un câble Ethernet"
    assert doc["statut"] == "finalise"
    assert doc["co_intervention"] is True
    assert doc["co_auteurs"] == ["Marie Bernard"]
    assert doc["referentiel"] == {"identifiant": "2tne-ciel", "formation": "2TNE"}
    assert doc["contexte"][0]["libelle"] == "Description du contexte"
    crit = doc["activites"][0]["competences"][0]["criteres"]
    assert crit[0]["indicateurs"] == ["Continuité OK"]
    assert crit[1]["savoir_etre"] is True
    assert doc["ressources"][0]["nom"] == "schema.pdf"


def test_json_sans_referentiel() -> None:
    data: dict[str, Any] = {**_DATA, "referentiel": None, "activites": []}
    doc = json.loads(rendre_json(data))
    assert doc["referentiel"] is None
    assert doc["activites"] == []


# ── Markdown ─────────────────────────────────────────────────────────────────

def test_markdown_contient_les_sections() -> None:
    md = rendre_markdown(_DATA)
    assert md.startswith("# Créer un câble Ethernet")
    assert "*Statut : Finalisé*" in md
    assert "· 2tne-ciel" in md
    assert "*Co-intervention : Marie Bernard*" in md
    for section in ("## Intention", "## Objectifs", "## Contexte", "## Liaison au référentiel",
                    "## Ressources"):
        assert section in md
    assert "### A1 — Câblage" in md
    assert "- **C03** Câbler" in md
    assert "  - Le câble est conforme" in md
    assert "    - ✓ Continuité OK" in md
    assert "*(savoir-être)*" in md          # critère savoir-être marqué
    assert "- schema.pdf (application/pdf)" in md


def test_markdown_minimal_sans_referentiel_ni_co_intervention() -> None:
    data: dict[str, Any] = {
        "scenario": {"Titre": "Séance libre", "Statut": "finalise", "CoIntervention": 0,
                     "Intention": None, "Objectifs": None},
        "referentiel": None, "co_auteurs": [], "contexte": [], "activites": [], "ressources": [],
    }
    md = rendre_markdown(data)
    assert md.startswith("# Séance libre")
    assert "Co-intervention" not in md
    assert "## Liaison au référentiel" not in md   # pas d'activité → section absente
    assert md.endswith("\n")
