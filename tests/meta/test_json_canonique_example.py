# pyright: strict
"""Test méta : l'exemple CIEL 2TNE valide contre le schéma et respecte les invariants.

Dogfoode la chaîne contrat (ticket 02) → schéma (ticket 04) → exemple (ticket 03) et
préfigure la validation sémantique que fera l'importeur (ADR-008).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

import jsonschema
import pytest

pytestmark = pytest.mark.meta

ROOT = Path(__file__).resolve().parents[2]
SPEC = ROOT / "docs" / "specs" / "json-canonique"
SCHEMA = SPEC / "schemas" / "schema-json-canonique-referentiel-niveau-classe.json"
EXAMPLE = SPEC / "examples" / "json-canonique-ciel-2tne.json"
STARTER_SCHEMA = SPEC / "schemas" / "schema-json-canonique-parcours.json"
STARTER_EXAMPLE = SPEC / "examples" / "json-canonique-welcome-reseau.json"
STARTER_BUNDLE = ROOT / "sources" / "starters" / "welcome-reseau"


def _load(path: Path) -> dict[str, Any]:
    return cast("dict[str, Any]", json.loads(path.read_text(encoding="utf-8")))


def test_exemple_valide_contre_le_schema() -> None:
    """Validation structurelle (JSON Schema) — lève ValidationError si non conforme."""
    jsonschema.validate(instance=_load(EXAMPLE), schema=_load(SCHEMA))


def test_exemple_invariants_semantiques() -> None:
    """Unicité des id/codes et résolution des références (ce que vérifiera l'importeur)."""
    doc = _load(EXAMPLE)
    activites: list[Any] = doc["activites_professionnelles"]
    competences: list[Any] = doc["competences"]

    pole_ids = [cast(str, p["id"]) for p in doc["poles_activites"]]
    act_codes = [cast(str, a["code"]) for a in activites]
    comp_codes = [cast(str, c["code"]) for c in competences]
    cc_codes = [cast(str, c["code"]) for c in doc["famille_competences"]]
    ra_ids = [cast(str, r["id"]) for a in activites for r in a.get("resultats_attendus", [])]
    cr_ids = [cast(str, c["id"]) for k in competences for c in k.get("criteres_evaluation", [])]

    # Unicité
    for seq in (pole_ids, act_codes, comp_codes, cc_codes, ra_ids, cr_ids):
        assert len(seq) == len(set(seq))

    poles, acts, comps = set(pole_ids), set(act_codes), set(comp_codes)
    ccs, ras, crs = set(cc_codes), set(ra_ids), set(cr_ids)

    # Références résolues
    for a in activites:
        assert cast(str, a["pole_id"]) in poles
    rel: dict[str, Any] = doc["relations"]
    for r in rel["activites_competences"]:
        assert cast(str, r["activite"]) in acts
        assert all(cast(str, x) in comps for x in r["competences"])
    for r in rel["competences_criteres"]:
        assert cast(str, r["competence"]) in comps
        assert all(cast(str, x) in crs for x in r["criteres"])
    for r in rel["activites_resultats_attendus"]:
        assert cast(str, r["activite"]) in acts
        assert all(cast(str, x) in ras for x in r["resultats"])
    for r in rel["cc_competences"]:
        assert cast(str, r["cc"]) in ccs
        assert all(cast(str, x) in comps for x in r["competences"])
    for ind in doc["indicateurs_reussite"]:
        if "ref" in ind:
            assert cast(str, ind["ref"]) in (ras | crs)


def test_starter_valide_contre_le_schema() -> None:
    """Le manifeste Welcome Réseau valide contre le schéma starter_welcome."""
    jsonschema.validate(instance=_load(STARTER_EXAMPLE), schema=_load(STARTER_SCHEMA))


def test_starter_invariants_semantiques() -> None:
    """Ordre contigu, bonne_reponse ∈ choix, fichiers référencés présents dans le bundle."""
    doc = _load(STARTER_EXAMPLE)
    paliers: list[Any] = doc["paliers"]

    ordres = [cast(int, p["ordre"]) for p in paliers]
    assert ordres == list(range(1, len(ordres) + 1))

    for p in paliers:
        # ADR-022 : le dossier technique est un conteneur de ressources typées ;
        # les ressources référençant un fichier doivent exister dans le bundle.
        for ressource in p["dossier_technique"]["ressources"]:
            fichier = ressource.get("fichier")
            if fichier is not None:
                assert (STARTER_BUNDLE / cast(str, fichier)).is_file()
        qcm = p.get("qcm")
        if qcm is not None:
            for question in qcm["questions"]:
                lettres = {cast(str, c["lettre"]) for c in question["choix"]}
                assert cast(str, question["bonne_reponse"]) in lettres
        for image in p.get("images", []):
            assert (STARTER_BUNDLE / cast(str, image["fichier"])).is_file()
