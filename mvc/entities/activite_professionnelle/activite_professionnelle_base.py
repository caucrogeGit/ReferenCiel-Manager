"""FICHIER GENERE PAR FORGE.
Base regenerable de l'entite ActiviteProfessionnelle.
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


class ActiviteProfessionnelleBase:
    """Classe de base regenerable de ActiviteProfessionnelle."""

    def __init__(self, code, intitule, referentiel_id, pole_id, created_at, updated_at, id=None, conditions_exercice=None):
        self.code = code
        self.intitule = intitule
        self.referentiel_id = referentiel_id
        self.pole_id = pole_id
        self.created_at = created_at
        self.updated_at = updated_at
        self.id = id
        self.conditions_exercice = conditions_exercice

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
    def code(self):
        return self._code

    @code.setter
    @typed(str)
    def code(self, value):
        if value is None:
            raise ValidationError("code", 'La propriété "code" ne peut pas être nulle.')
        self._code = value

    @property
    def intitule(self):
        return self._intitule

    @intitule.setter
    @typed(str)
    def intitule(self, value):
        if value is None:
            raise ValidationError("intitule", 'La propriété "intitule" ne peut pas être nulle.')
        self._intitule = value

    @property
    def conditions_exercice(self):
        return self._conditions_exercice

    @conditions_exercice.setter
    @typed(str)
    @nullable
    def conditions_exercice(self, value):
        if value is None:
            self._conditions_exercice = None
            return
        self._conditions_exercice = value

    @property
    def referentiel_id(self):
        return self._referentiel_id

    @referentiel_id.setter
    @typed(int)
    def referentiel_id(self, value):
        if value is None:
            raise ValidationError("referentiel_id", 'La propriété "referentiel_id" ne peut pas être nulle.')
        self._referentiel_id = value

    @property
    def pole_id(self):
        return self._pole_id

    @pole_id.setter
    @typed(int)
    def pole_id(self, value):
        if value is None:
            raise ValidationError("pole_id", 'La propriété "pole_id" ne peut pas être nulle.')
        self._pole_id = value

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
            "code": self.code,
            "intitule": self.intitule,
            "conditions_exercice": self.conditions_exercice,
            "referentiel_id": self.referentiel_id,
            "pole_id": self.pole_id,
            "created_at": None if self.created_at is None else self.created_at.isoformat(),
            "updated_at": None if self.updated_at is None else self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ActiviteProfessionnelleBase":
        return cls(
            id=data["id"],
            code=data["code"],
            intitule=data["intitule"],
            conditions_exercice=data["conditions_exercice"],
            referentiel_id=data["referentiel_id"],
            pole_id=data["pole_id"],
            created_at=cls._coerce_datetime(data.get("created_at")),
            updated_at=cls._coerce_datetime(data.get("updated_at")),
        )

    def __repr__(self) -> str:
        return f"ActiviteProfessionnelleBase(id={self.id!r}, code={self.code!r}, intitule={self.intitule!r}, conditions_exercice={self.conditions_exercice!r}, referentiel_id={self.referentiel_id!r}, pole_id={self.pole_id!r}, created_at={self.created_at!r}, updated_at={self.updated_at!r})"

