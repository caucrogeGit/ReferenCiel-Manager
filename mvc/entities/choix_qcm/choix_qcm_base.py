"""FICHIER GENERE PAR FORGE.
Base regenerable de l'entite ChoixQCM.
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


class ChoixQCMBase:
    """Classe de base regenerable de ChoixQCM."""

    def __init__(self, lettre, texte, question_id, created_at, updated_at, id=None):
        self.lettre = lettre
        self.texte = texte
        self.question_id = question_id
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
    def lettre(self):
        return self._lettre

    @lettre.setter
    @typed(str)
    def lettre(self, value):
        if value is None:
            raise ValidationError("lettre", 'La propriété "lettre" ne peut pas être nulle.')
        self._lettre = value

    @property
    def texte(self):
        return self._texte

    @texte.setter
    @typed(str)
    def texte(self, value):
        if value is None:
            raise ValidationError("texte", 'La propriété "texte" ne peut pas être nulle.')
        self._texte = value

    @property
    def question_id(self):
        return self._question_id

    @question_id.setter
    @typed(int)
    def question_id(self, value):
        if value is None:
            raise ValidationError("question_id", 'La propriété "question_id" ne peut pas être nulle.')
        self._question_id = value

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
            "lettre": self.lettre,
            "texte": self.texte,
            "question_id": self.question_id,
            "created_at": None if self.created_at is None else self.created_at.isoformat(),
            "updated_at": None if self.updated_at is None else self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ChoixQCMBase":
        return cls(
            id=data["id"],
            lettre=data["lettre"],
            texte=data["texte"],
            question_id=data["question_id"],
            created_at=cls._coerce_datetime(data.get("created_at")),
            updated_at=cls._coerce_datetime(data.get("updated_at")),
        )

    def __repr__(self) -> str:
        return f"ChoixQCMBase(id={self.id!r}, lettre={self.lettre!r}, texte={self.texte!r}, question_id={self.question_id!r}, created_at={self.created_at!r}, updated_at={self.updated_at!r})"

