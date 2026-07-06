# pyright: strict
"""Tests méta : cohérence documentaire et discipline projet (ADR-006).

Ne testent pas le métier ni le framework : ils garantissent que la documentation
et les décisions restent cohérentes au fil de la progression (au standard Forge).
"""

from __future__ import annotations

from pathlib import Path
from typing import cast

import pytest
import yaml

pytestmark = pytest.mark.meta

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs"


def _collect_nav_md(nav: object, acc: list[str]) -> None:
    """Collecte récursivement les chemins .md référencés dans la nav mkdocs."""
    if isinstance(nav, str):
        if nav.endswith(".md"):
            acc.append(nav)
    elif isinstance(nav, list):
        for item in cast("list[object]", nav):
            _collect_nav_md(item, acc)
    elif isinstance(nav, dict):
        for value in cast("dict[str, object]", nav).values():
            _collect_nav_md(value, acc)


def test_every_doc_page_is_in_mkdocs_nav() -> None:
    """Aucune page orpheline, aucune entrée de nav fantôme (comme `--strict`)."""
    cfg = yaml.safe_load((ROOT / "mkdocs.yml").read_text(encoding="utf-8"))
    nav_paths: list[str] = []
    _collect_nav_md(cfg.get("nav", []), nav_paths)
    nav_set = {(DOCS / rel).resolve() for rel in nav_paths}
    on_disk = {p.resolve() for p in DOCS.rglob("*.md")}

    orphans = sorted(str(p.relative_to(ROOT)) for p in on_disk - nav_set)
    ghosts = sorted(str(p.relative_to(ROOT)) for p in nav_set - on_disk)
    assert not orphans, f"pages doc absentes de la nav mkdocs : {orphans}"
    assert not ghosts, f"nav mkdocs référence des fichiers absents : {ghosts}"


def test_adr_numbering_is_contiguous() -> None:
    """Les ADR sont numérotés 001, 002, … sans trou (discipline Forge)."""
    adrs = sorted((DOCS / "adr").glob("[0-9][0-9][0-9]-*.md"))
    # 000-template.md est le gabarit livré par Forge, pas une décision.
    nums = [n for n in (int(p.name[:3]) for p in adrs) if n != 0]
    assert nums, "aucun ADR trouvé"
    assert nums == list(range(1, len(nums) + 1)), f"numérotation ADR non contiguë : {nums}"


def test_cadrage_key_documents_present() -> None:
    """Les documents de cadrage prioritaires existent."""
    required = [
        "index.md",
        "cadrage/instructions.md",
        "cadrage/cadre-projet-referenciel-manager.md",
        "roadmap/roadmap-referenciel-manager.md",
        "tickets/README.md",
        "specs/json-canonique/README.md",
        "specs/json-canonique/registre-des-sources.md",
    ]
    missing = [rel for rel in required if not (DOCS / rel).is_file()]
    assert not missing, f"documents de cadrage manquants : {missing}"
