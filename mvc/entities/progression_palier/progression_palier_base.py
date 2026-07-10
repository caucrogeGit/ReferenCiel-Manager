"""FICHIER GENERE PAR FORGE.
Base regenerable de l'entite ProgressionPalier.
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


class ProgressionPalierBase:
    """Classe de base regenerable de ProgressionPalier."""

    def __init__(self, statut, progression_eleve_id, palier_id, created_at, updated_at, id=None):
        self.statut = statut
        self.progression_eleve_id = progression_eleve_id
        self.palier_id = palier_id
        self.created_at = created_at
        self.updated_at = updated_at
        self.id = id

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
    def statut(self):
        return self._statut

    @statut.setter
    @typed(str)
    def statut(self, value):
        if value is None:
            raise ValidationError("statut", 'La propriété "statut" ne peut pas être nulle.')
        self._statut = value

    @property
    def progression_eleve_id(self):
        return self._progression_eleve_id

    @progression_eleve_id.setter
    @typed(int)
    def progression_eleve_id(self, value):
        if value is None:
            raise ValidationError("progression_eleve_id", 'La propriété "progression_eleve_id" ne peut pas être nulle.')
        self._progression_eleve_id = value

    @property
    def palier_id(self):
        return self._palier_id

    @palier_id.setter
    @typed(int)
    def palier_id(self, value):
        if value is None:
            raise ValidationError("palier_id", 'La propriété "palier_id" ne peut pas être nulle.')
        self._palier_id = value

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
            "statut": self.statut,
            "progression_eleve_id": self.progression_eleve_id,
            "palier_id": self.palier_id,
            "created_at": None if self.created_at is None else self.created_at.isoformat(),
            "updated_at": None if self.updated_at is None else self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ProgressionPalierBase":
        return cls(
            id=data["id"],
            statut=data["statut"],
            progression_eleve_id=data["progression_eleve_id"],
            palier_id=data["palier_id"],
            created_at=cls._coerce_datetime(data.get("created_at")),
            updated_at=cls._coerce_datetime(data.get("updated_at")),
        )

    def __repr__(self) -> str:
        return f"ProgressionPalierBase(id={self.id!r}, statut={self.statut!r}, progression_eleve_id={self.progression_eleve_id!r}, palier_id={self.palier_id!r}, created_at={self.created_at!r}, updated_at={self.updated_at!r})"

