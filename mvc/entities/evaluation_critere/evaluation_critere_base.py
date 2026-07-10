"""FICHIER GENERE PAR FORGE.
Base regenerable de l'entite EvaluationCritere.
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


class EvaluationCritereBase:
    """Classe de base regenerable de EvaluationCritere."""

    def __init__(self, niveau, evaluation_activite_id, critere_id, created_at, updated_at, id=None):
        self.niveau = niveau
        self.evaluation_activite_id = evaluation_activite_id
        self.critere_id = critere_id
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
    def niveau(self):
        return self._niveau

    @niveau.setter
    @typed(str)
    def niveau(self, value):
        if value is None:
            raise ValidationError("niveau", 'La propriété "niveau" ne peut pas être nulle.')
        self._niveau = value

    @property
    def evaluation_activite_id(self):
        return self._evaluation_activite_id

    @evaluation_activite_id.setter
    @typed(int)
    def evaluation_activite_id(self, value):
        if value is None:
            raise ValidationError("evaluation_activite_id", 'La propriété "evaluation_activite_id" ne peut pas être nulle.')
        self._evaluation_activite_id = value

    @property
    def critere_id(self):
        return self._critere_id

    @critere_id.setter
    @typed(int)
    def critere_id(self, value):
        if value is None:
            raise ValidationError("critere_id", 'La propriété "critere_id" ne peut pas être nulle.')
        self._critere_id = value

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
            "niveau": self.niveau,
            "evaluation_activite_id": self.evaluation_activite_id,
            "critere_id": self.critere_id,
            "created_at": None if self.created_at is None else self.created_at.isoformat(),
            "updated_at": None if self.updated_at is None else self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EvaluationCritereBase":
        return cls(
            id=data["id"],
            niveau=data["niveau"],
            evaluation_activite_id=data["evaluation_activite_id"],
            critere_id=data["critere_id"],
            created_at=cls._coerce_datetime(data.get("created_at")),
            updated_at=cls._coerce_datetime(data.get("updated_at")),
        )

    def __repr__(self) -> str:
        return f"EvaluationCritereBase(id={self.id!r}, niveau={self.niveau!r}, evaluation_activite_id={self.evaluation_activite_id!r}, critere_id={self.critere_id!r}, created_at={self.created_at!r}, updated_at={self.updated_at!r})"

