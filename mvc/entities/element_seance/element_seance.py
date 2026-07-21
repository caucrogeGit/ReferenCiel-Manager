"""Classe metier manuelle pour ElementSeance (ADR-032, phase B).

Élément ordonné du déroulé d'une séance. Polymorphe : contenu libre pour la
plupart des types, référence à un QCM ou une checklist existants pour ces deux.
"""

from .element_seance_base import ElementSeanceBase


class ElementSeance(ElementSeanceBase):
    """Point d'extension metier pour ElementSeance."""

    pass
