# pyright: strict
"""Validation d'un JSON canonique contre son schéma (ADR-008 : la porte d'entrée).

Un fichier non conforme est **refusé** avec des messages lisibles avant tout import.
Le schéma vit dans `docs/specs/json-canonique/schemas/` (ticket 04).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import jsonschema

_SCHEMA_DIR = Path("docs/specs/json-canonique/schemas")
_SCHEMA_REFERENTIEL = _SCHEMA_DIR / "schema-json-canonique-referentiel-niveau-classe.json"


def _load_schema(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_referentiel_canonical(data: Any) -> list[str]:
    """Valide `data` contre le schéma du référentiel niveau-classe (Draft 2020-12).

    Retourne la liste triée des messages d'erreur (vide si le document est conforme).
    `jsonschema` n'étant pas typé, il est confiné derrière un `Any` explicite.
    """
    schema = _load_schema(_SCHEMA_REFERENTIEL)
    js: Any = jsonschema
    validator: Any = js.Draft202012Validator(schema)
    erreurs: list[str] = []
    for err in validator.iter_errors(data):
        chemin = "/".join(str(p) for p in err.path) or "(racine)"
        erreurs.append(f"{chemin} : {err.message}")
    return sorted(erreurs)
