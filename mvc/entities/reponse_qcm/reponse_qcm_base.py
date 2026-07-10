"""FICHIER GENERE PAR FORGE.
Base regenerable de l'entite ReponseQCM.
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


class ReponseQCMBase:
    """Classe de base regenerable de ReponseQCM."""

    def __init__(self, est_correcte, tentative_id, question_id, choix_id, created_at, updated_at, id=None):
        self.est_correcte = est_correcte
        self.tentative_id = tentative_id
        self.question_id = question_id
        self.choix_id = choix_id
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
    def est_correcte(self):
        return self._est_correcte

    @est_correcte.setter
    @typed(bool)
    def est_correcte(self, value):
        if value is None:
            raise ValidationError("est_correcte", 'La propriété "est_correcte" ne peut pas être nulle.')
        self._est_correcte = value

    @property
    def tentative_id(self):
        return self._tentative_id

    @tentative_id.setter
    @typed(int)
    def tentative_id(self, value):
        if value is None:
            raise ValidationError("tentative_id", 'La propriété "tentative_id" ne peut pas être nulle.')
        self._tentative_id = value

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
    def choix_id(self):
        return self._choix_id

    @choix_id.setter
    @typed(int)
    def choix_id(self, value):
        if value is None:
            raise ValidationError("choix_id", 'La propriété "choix_id" ne peut pas être nulle.')
        self._choix_id = value

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
            "est_correcte": self.est_correcte,
            "tentative_id": self.tentative_id,
            "question_id": self.question_id,
            "choix_id": self.choix_id,
            "created_at": None if self.created_at is None else self.created_at.isoformat(),
            "updated_at": None if self.updated_at is None else self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ReponseQCMBase":
        return cls(
            id=data["id"],
            est_correcte=data["est_correcte"],
            tentative_id=data["tentative_id"],
            question_id=data["question_id"],
            choix_id=data["choix_id"],
            created_at=cls._coerce_datetime(data.get("created_at")),
            updated_at=cls._coerce_datetime(data.get("updated_at")),
        )

    def __repr__(self) -> str:
        return f"ReponseQCMBase(id={self.id!r}, est_correcte={self.est_correcte!r}, tentative_id={self.tentative_id!r}, question_id={self.question_id!r}, choix_id={self.choix_id!r}, created_at={self.created_at!r}, updated_at={self.updated_at!r})"

