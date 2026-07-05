# pyright: strict
"""Tests de fumée : le squelette Forge reste sain, sans backend BDD (ADR-006).

Exercent le framework (banc d'essai, ADR-005) sans dépendre d'une base :
`forge project:check` doit rester conforme, et le registre d'opt-ins doit
respecter son contrat.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.smoke
def test_optins_registry_contract() -> None:
    """`optins/registry.py` (ADR-061) expose son contrat public, typé strict."""
    from optins.registry import BACKEND, ENABLED_OPTINS, register_optins

    assert BACKEND is None or isinstance(BACKEND, str)
    assert isinstance(ENABLED_OPTINS, dict)
    assert callable(register_optins)


@pytest.mark.smoke
def test_forge_project_check_is_conformant() -> None:
    """`forge project:check` valide la structure du projet (0 = conforme)."""
    forge = Path(sys.executable).parent / "forge"
    if not forge.exists():
        pytest.skip("binaire forge introuvable dans l'environnement")
    result = subprocess.run(
        [str(forge), "project:check"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "conforme" in result.stdout.lower()
