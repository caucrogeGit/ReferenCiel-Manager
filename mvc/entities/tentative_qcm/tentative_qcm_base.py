"""FICHIER GENERE PAR FORGE.
Base regenerable de l'entite TentativeQCM.
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


class TentativeQCMBase:
    """Classe de base regenerable de TentativeQCM."""

    def __init__(self, numero_tentative, score, validee, date_tentative, progression_palier_id, created_at, updated_at, id=None):
        self.numero_tentative = numero_tentative
        self.score = score
        self.validee = validee
        self.date_tentative = date_tentative
        self.progression_palier_id = progression_palier_id
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
    def numero_tentative(self):
        return self._numero_tentative

    @numero_tentative.setter
    @typed(int)
    def numero_tentative(self, value):
        if value is None:
            raise ValidationError("numero_tentative", 'La propriété "numero_tentative" ne peut pas être nulle.')
        self._numero_tentative = value

    @property
    def score(self):
        return self._score

    @score.setter
    @typed(int)
    def score(self, value):
        if value is None:
            raise ValidationError("score", 'La propriété "score" ne peut pas être nulle.')
        self._score = value

    @property
    def validee(self):
        return self._validee

    @validee.setter
    @typed(bool)
    def validee(self, value):
        if value is None:
            raise ValidationError("validee", 'La propriété "validee" ne peut pas être nulle.')
        self._validee = value

    @property
    def date_tentative(self):
        return self._date_tentative

    @date_tentative.setter
    @typed(datetime)
    def date_tentative(self, value):
        if value is None:
            raise ValidationError("date_tentative", 'La propriété "date_tentative" ne peut pas être nulle.')
        self._date_tentative = value

    @property
    def progression_palier_id(self):
        return self._progression_palier_id

    @progression_palier_id.setter
    @typed(int)
    def progression_palier_id(self, value):
        if value is None:
            raise ValidationError("progression_palier_id", 'La propriété "progression_palier_id" ne peut pas être nulle.')
        self._progression_palier_id = value

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
            "numero_tentative": self.numero_tentative,
            "score": self.score,
            "validee": self.validee,
            "date_tentative": None if self.date_tentative is None else self.date_tentative.isoformat(),
            "progression_palier_id": self.progression_palier_id,
            "created_at": None if self.created_at is None else self.created_at.isoformat(),
            "updated_at": None if self.updated_at is None else self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TentativeQCMBase":
        return cls(
            id=data["id"],
            numero_tentative=data["numero_tentative"],
            score=data["score"],
            validee=data["validee"],
            date_tentative=cls._coerce_datetime(data.get("date_tentative")),
            progression_palier_id=data["progression_palier_id"],
            created_at=cls._coerce_datetime(data.get("created_at")),
            updated_at=cls._coerce_datetime(data.get("updated_at")),
        )

    def __repr__(self) -> str:
        return f"TentativeQCMBase(id={self.id!r}, numero_tentative={self.numero_tentative!r}, score={self.score!r}, validee={self.validee!r}, date_tentative={self.date_tentative!r}, progression_palier_id={self.progression_palier_id!r}, created_at={self.created_at!r}, updated_at={self.updated_at!r})"

