"""FICHIER GENERE PAR FORGE.
Base regenerable de l'entite SequenceConnaissance.
Ne pas y ajouter de logique metier manuelle.
"""

from __future__ import annotations

from typing import Any

from datetime import datetime

from core.validation import (
    ValidationError,
    nullable,
    typed,
)


class SequenceConnaissanceBase:
    """Classe de base regenerable de SequenceConnaissance."""

    def __init__(self, sequence_id, connaissance_id, created_at, updated_at, id=None, niveau_cible=None, statut=None, commentaire=None):
        self.sequence_id = sequence_id
        self.connaissance_id = connaissance_id
        self.created_at = created_at
        self.updated_at = updated_at
        self.id = id
        self.niveau_cible = niveau_cible
        self.statut = statut
        self.commentaire = commentaire

    @staticmethod
    def _coerce_datetime(value):
        if value is None or isinstance(value, datetime):
            return value
        return datetime.fromisoformat(value)

    @property
    def id(self):
        return self._id

    @id.setter
    @typed(int)
    @nullable
    def id(self, value):
        if value is None:
            self._id = None
            return
        self._id = value

    @property
    def sequence_id(self):
        return self._sequence_id

    @sequence_id.setter
    @typed(int)
    def sequence_id(self, value):
        if value is None:
            raise ValidationError("sequence_id", 'La propriété "sequence_id" ne peut pas être nulle.')
        self._sequence_id = value

    @property
    def connaissance_id(self):
        return self._connaissance_id

    @connaissance_id.setter
    @typed(int)
    def connaissance_id(self, value):
        if value is None:
            raise ValidationError("connaissance_id", 'La propriété "connaissance_id" ne peut pas être nulle.')
        self._connaissance_id = value

    @property
    def niveau_cible(self):
        return self._niveau_cible

    @niveau_cible.setter
    @typed(int)
    @nullable
    def niveau_cible(self, value):
        if value is None:
            self._niveau_cible = None
            return
        self._niveau_cible = value

    @property
    def statut(self):
        return self._statut

    @statut.setter
    @typed(str)
    @nullable
    def statut(self, value):
        if value is None:
            self._statut = None
            return
        self._statut = value

    @property
    def commentaire(self):
        return self._commentaire

    @commentaire.setter
    @typed(str)
    @nullable
    def commentaire(self, value):
        if value is None:
            self._commentaire = None
            return
        self._commentaire = value

    @property
    def created_at(self):
        return self._created_at

    @created_at.setter
    @typed(datetime)
    def created_at(self, value):
        if value is None:
            raise ValidationError("created_at", 'La propriété "created_at" ne peut pas être nulle.')
        self._created_at = value

    @property
    def updated_at(self):
        return self._updated_at

    @updated_at.setter
    @typed(datetime)
    def updated_at(self, value):
        if value is None:
            raise ValidationError("updated_at", 'La propriété "updated_at" ne peut pas être nulle.')
        self._updated_at = value

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "sequence_id": self.sequence_id,
            "connaissance_id": self.connaissance_id,
            "niveau_cible": self.niveau_cible,
            "statut": self.statut,
            "commentaire": self.commentaire,
            "created_at": None if self.created_at is None else self.created_at.isoformat(),
            "updated_at": None if self.updated_at is None else self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SequenceConnaissanceBase":
        return cls(
            id=data["id"],
            sequence_id=data["sequence_id"],
            connaissance_id=data["connaissance_id"],
            niveau_cible=data["niveau_cible"],
            statut=data["statut"],
            commentaire=data["commentaire"],
            created_at=cls._coerce_datetime(data.get("created_at")),
            updated_at=cls._coerce_datetime(data.get("updated_at")),
        )

    def __repr__(self) -> str:
        return f"SequenceConnaissanceBase(id={self.id!r}, sequence_id={self.sequence_id!r}, connaissance_id={self.connaissance_id!r}, niveau_cible={self.niveau_cible!r}, statut={self.statut!r}, commentaire={self.commentaire!r}, created_at={self.created_at!r}, updated_at={self.updated_at!r})"

