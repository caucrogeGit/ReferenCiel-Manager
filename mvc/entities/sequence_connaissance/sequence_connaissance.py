"""Classe metier manuelle pour SequenceConnaissance (ADR-028).

Lien entre une séquence et une connaissance du référentiel, portant les données
pédagogiques propres à la séquence : niveau cible (≠ niveau officiel), statut
dans la progression, commentaire.
"""

from .sequence_connaissance_base import SequenceConnaissanceBase


class SequenceConnaissance(SequenceConnaissanceBase):
    """Point d'extension metier pour SequenceConnaissance."""

    pass
