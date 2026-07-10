"""FICHIER GENERE PAR FORGE.
Base regenerable de l'entite EvaluationActivite.
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


class EvaluationActiviteBase:
    """Classe de base regenerable de EvaluationActivite."""

    def __init__(self, date_evaluation, progression_palier_id, activite_id, professeur_id, created_at, updated_at, id=None, appreciation=None):
        self.date_evaluation = date_evaluation
        self.progression_palier_id = progression_palier_id
        self.activite_id = activite_id
        self.professeur_id = professeur_id
        self.created_at = created_at
        self.updated_at = updated_at
        self.id = id
        self.appreciation = appreciation

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
    def date_evaluation(self):
        return self._date_evaluation

    @date_evaluation.setter
    @typed(datetime)
    def date_evaluation(self, value):
        if value is None:
            raise ValidationError("date_evaluation", 'La propriété "date_evaluation" ne peut pas être nulle.')
        self._date_evaluation = value

    @property
    def appreciation(self):
        return self._appreciation

    @appreciation.setter
    @typed(str)
    @nullable
    def appreciation(self, value):
        if value is None:
            self._appreciation = None
            return
        self._appreciation = value

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
    def activite_id(self):
        return self._activite_id

    @activite_id.setter
    @typed(int)
    def activite_id(self, value):
        if value is None:
            raise ValidationError("activite_id", 'La propriété "activite_id" ne peut pas être nulle.')
        self._activite_id = value

    @property
    def professeur_id(self):
        return self._professeur_id

    @professeur_id.setter
    @typed(int)
    def professeur_id(self, value):
        if value is None:
            raise ValidationError("professeur_id", 'La propriété "professeur_id" ne peut pas être nulle.')
        self._professeur_id = value

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
            "date_evaluation": None if self.date_evaluation is None else self.date_evaluation.isoformat(),
            "appreciation": self.appreciation,
            "progression_palier_id": self.progression_palier_id,
            "activite_id": self.activite_id,
            "professeur_id": self.professeur_id,
            "created_at": None if self.created_at is None else self.created_at.isoformat(),
            "updated_at": None if self.updated_at is None else self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EvaluationActiviteBase":
        return cls(
            id=data["id"],
            date_evaluation=cls._coerce_datetime(data.get("date_evaluation")),
            appreciation=data["appreciation"],
            progression_palier_id=data["progression_palier_id"],
            activite_id=data["activite_id"],
            professeur_id=data["professeur_id"],
            created_at=cls._coerce_datetime(data.get("created_at")),
            updated_at=cls._coerce_datetime(data.get("updated_at")),
        )

    def __repr__(self) -> str:
        return f"EvaluationActiviteBase(id={self.id!r}, date_evaluation={self.date_evaluation!r}, appreciation={self.appreciation!r}, progression_palier_id={self.progression_palier_id!r}, activite_id={self.activite_id!r}, professeur_id={self.professeur_id!r}, created_at={self.created_at!r}, updated_at={self.updated_at!r})"

