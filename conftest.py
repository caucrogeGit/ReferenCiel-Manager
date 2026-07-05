# pyright: strict
"""Configuration pytest du projet.

Rend la racine du projet importable (pour `import optins.registry`, etc.) et
sert de point d'ancrage à la découverte des tests. Aucun import lourd ici :
l'app n'a pas encore de backend BDD (ADR-004), les tests restent agnostiques.
"""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
