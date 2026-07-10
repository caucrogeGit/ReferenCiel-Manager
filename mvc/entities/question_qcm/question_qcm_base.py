"""FICHIER GENERE PAR FORGE.
Base regenerable de l'entite QuestionQCM.
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


class QuestionQCMBase:
    """Classe de base regenerable de QuestionQCM."""

    def __init__(self, numero, enonce, bonne_reponse, qcm_id, created_at, updated_at, id=None):
        self.numero = numero
        self.enonce = enonce
        self.bonne_reponse = bonne_reponse
        self.qcm_id = qcm_id
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
    def numero(self):
        return self._numero

    @numero.setter
    @typed(int)
    def numero(self, value):
        if value is None:
            raise ValidationError("numero", 'La propriété "numero" ne peut pas être nulle.')
        self._numero = value

    @property
    def enonce(self):
        return self._enonce

    @enonce.setter
    @typed(str)
    def enonce(self, value):
        if value is None:
            raise ValidationError("enonce", 'La propriété "enonce" ne peut pas être nulle.')
        self._enonce = value

    @property
    def bonne_reponse(self):
        return self._bonne_reponse

    @bonne_reponse.setter
    @typed(str)
    def bonne_reponse(self, value):
        if value is None:
            raise ValidationError("bonne_reponse", 'La propriété "bonne_reponse" ne peut pas être nulle.')
        self._bonne_reponse = value

    @property
    def qcm_id(self):
        return self._qcm_id

    @qcm_id.setter
    @typed(int)
    def qcm_id(self, value):
        if value is None:
            raise ValidationError("qcm_id", 'La propriété "qcm_id" ne peut pas être nulle.')
        self._qcm_id = value

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
            "numero": self.numero,
            "enonce": self.enonce,
            "bonne_reponse": self.bonne_reponse,
            "qcm_id": self.qcm_id,
            "created_at": None if self.created_at is None else self.created_at.isoformat(),
            "updated_at": None if self.updated_at is None else self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "QuestionQCMBase":
        return cls(
            id=data["id"],
            numero=data["numero"],
            enonce=data["enonce"],
            bonne_reponse=data["bonne_reponse"],
            qcm_id=data["qcm_id"],
            created_at=cls._coerce_datetime(data.get("created_at")),
            updated_at=cls._coerce_datetime(data.get("updated_at")),
        )

    def __repr__(self) -> str:
        return f"QuestionQCMBase(id={self.id!r}, numero={self.numero!r}, enonce={self.enonce!r}, bonne_reponse={self.bonne_reponse!r}, qcm_id={self.qcm_id!r}, created_at={self.created_at!r}, updated_at={self.updated_at!r})"

