"""FICHIER GENERE PAR FORGE.
Base regenerable de l'entite InscriptionEleve.
Ne pas y ajouter de logique metier manuelle.
"""

from __future__ import annotations

from typing import Any

from datetime import date, datetime

from core.validation import (
    ValidationError,
    nullable,
    typed,
)


class InscriptionEleveBase:
    """Classe de base regenerable de InscriptionEleve."""

    def __init__(self, created_at, updated_at, id=None, date_inscription=None):
        self.created_at = created_at
        self.updated_at = updated_at
        self.id = id
        self.date_inscription = date_inscription

    @staticmethod
    def _coerce_date(value):
        if value is None or isinstance(value, date):
            return value
        return date.fromisoformat(value)

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
    def date_inscription(self):
        return self._date_inscription

    @date_inscription.setter
    @typed(date)
    @nullable
    def date_inscription(self, value):
        if value is None:
            self._date_inscription = None
            return
        self._date_inscription = value

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
            "date_inscription": None if self.date_inscription is None else self.date_inscription.isoformat(),
            "created_at": None if self.created_at is None else self.created_at.isoformat(),
            "updated_at": None if self.updated_at is None else self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "InscriptionEleveBase":
        return cls(
            id=data["id"],
            date_inscription=cls._coerce_date(data.get("date_inscription")),
            created_at=cls._coerce_datetime(data.get("created_at")),
            updated_at=cls._coerce_datetime(data.get("updated_at")),
        )

    def __repr__(self) -> str:
        return f"InscriptionEleveBase(id={self.id!r}, date_inscription={self.date_inscription!r}, created_at={self.created_at!r}, updated_at={self.updated_at!r})"

