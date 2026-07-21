# pyright: strict
"""Export d'une séquence en Markdown et JSON (ADR-028 / ADR-030).

Les formatters (`rendre_markdown`, `rendre_json`) sont **purs** : ils prennent le
dict assemblé, sans base — donc exécutables en CI.
"""
from __future__ import annotations

import json
from typing import Any

from mvc.services.sequence_export import rendre_json, rendre_markdown

_DATA: dict[str, Any] = {
    "sequence": {
        "Titre": "Câblage réseau",
        "niveau_classe_id_label": "2nde CIEL",
        "Prerequis": "Lire un plan",
        "PositionnementProgression": "Milieu de progression",
        "DureeEstimee": "3 semaines",
        "ModalitesEvaluation": "QCM + dossier",
    },
    "connaissances": [
        {
            "code": "C06", "intitule": "Valider la conformité",
            "connaissances": [
                {"libelle": "Réseaux informatiques", "niveau_officiel": 3,
                 "niveau_cible": 2, "statut": "mobilisee", "statut_label": "Mobilisée"},
            ],
        },
    ],
    "savoirs_libres": [],
    "seances": [
        {
            "Ordre": 1, "Titre": "Sertissage", "Theme": "RJ45",
            "ObjectifOperationnel": "Sertir un câble droit", "ConsigneGenerale": None,
            "DureeEstimeeMinutes": 90, "ModalitePedagogique": "Atelier",
            "ConditionRealisation": "Poste équipé", "ConditionValidation": None,
            "Remediation": None, "ProductionAttendue": "Câble testé",
            "elements": [
                {"Ordre": 1, "Type": "consigne", "Titre": "Présentation",
                 "Contenu": "Vous intervenez…", "DureeMinutes": 10, "Obligatoire": 1},
                {"Ordre": 2, "Type": "qcm", "Titre": "QCM de compréhension",
                 "Contenu": None, "DureeMinutes": 15, "Obligatoire": 0},
            ],
        },
    ],
}


def test_json_structure() -> None:
    doc = json.loads(rendre_json(_DATA))
    assert doc["titre"] == "Câblage réseau"
    assert doc["niveau"] == "2nde CIEL"
    assert doc["cadre"][0] == {"libelle": "Prérequis", "valeur": "Lire un plan"}
    grp = doc["connaissances"][0]
    assert grp["code"] == "C06"
    assert grp["connaissances"][0]["niveau_cible"] == 2
    seance = doc["seances"][0]
    assert seance["ordre"] == 1 and seance["titre"] == "Sertissage"
    assert seance["duree_minutes"] == 90
    assert seance["elements"][0]["type"] == "Consigne / présentation"
    assert seance["elements"][1]["obligatoire"] is False
    # champs : seuls les renseignés (ConsigneGenerale None → absent)
    libelles = [c["libelle"] for c in seance["champs"]]
    assert "Objectif opérationnel" in libelles and "Consigne générale" not in libelles


def test_markdown_sections() -> None:
    md = rendre_markdown(_DATA)
    assert md.startswith("# Câblage réseau")
    assert "*Niveau : 2nde CIEL*" in md
    for section in ("## Cadre institutionnel", "## Savoirs associés", "## Séances"):
        assert section in md
    assert "**Prérequis**" in md
    assert "### C06 — Valider la conformité" in md
    assert "- Réseaux informatiques — cible 2, officiel 3, Mobilisée" in md
    assert "### 1 — Sertissage (90 min)" in md
    assert "**Objectif opérationnel**" in md
    assert "**Déroulé :**" in md
    assert "1. **Consigne / présentation** — Présentation (10 min)" in md
    assert "*(facultatif)*" in md  # le QCM est facultatif


def test_markdown_savoirs_libres_hors_referentiel() -> None:
    data: dict[str, Any] = {
        **_DATA, "connaissances": [], "savoirs_libres": ["Lire un plan", "Multimètre"],
    }
    md = rendre_markdown(data)
    assert "## Savoirs associés" in md
    assert "- Lire un plan" in md
    doc = json.loads(rendre_json(data))
    assert doc["savoirs_libres"] == ["Lire un plan", "Multimètre"]
