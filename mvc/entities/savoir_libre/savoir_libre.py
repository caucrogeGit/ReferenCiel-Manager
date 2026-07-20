"""Classe metier manuelle pour SavoirLibre (ADR-030).

Savoir associé saisi librement par le professeur, pour une séquence sans
référentiel (aucune connaissance de référentiel où piocher).
"""

from .savoir_libre_base import SavoirLibreBase


class SavoirLibre(SavoirLibreBase):
    """Point d'extension metier pour SavoirLibre."""

    pass
