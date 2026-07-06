# pyright: strict
"""Test méta : le manifeste de squelette (ADR-009) ne référence que des chemins réels.

Garde-fou contre un manifeste périmé : si un chemin listé disparaît du projet, la
montée de squelette (`make skeleton-check`) le raterait silencieusement.
"""

from __future__ import annotations

from pathlib import Path

import pytest

pytestmark = pytest.mark.meta

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "tools" / "skeleton-manifest.txt"


def test_skeleton_manifest_paths_exist() -> None:
    """Chaque chemin non-commentaire du manifeste existe dans le projet."""
    lines = MANIFEST.read_text(encoding="utf-8").splitlines()
    paths = [s for line in lines if (s := line.strip()) and not s.startswith("#")]
    assert paths, "manifeste de squelette vide"
    missing = [p for p in paths if not (ROOT / p).exists()]
    assert not missing, f"manifeste référence des chemins absents : {missing}"
