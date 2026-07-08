"""FICHIER GENERE PAR FORGE.
Base regenerable de l'entite Classe.
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


class ClasseBase:
    """Classe de base regenerable de Classe."""

    def __init__(self, code, created_at, updated_at, id=None, libelle=None):
        self.code = code
        self.created_at = created_at
        self.updated_at = updated_at
        self.id = id
        self.libelle = libelle

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
    def libelle(self):
        return self._libelle

    @libelle.setter
    @typed(str)
    @nullable
    def libelle(self, value):
        if value is None:
            self._libelle = None
            return
        self._libelle = value

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
            "libelle": self.libelle,
            "created_at": None if self.created_at is None else self.created_at.isoformat(),
            "updated_at": None if self.updated_at is None else self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ClasseBase":
        return cls(
            id=data["id"],
            code=data["code"],
            libelle=data["libelle"],
            created_at=cls._coerce_datetime(data.get("created_at")),
            updated_at=cls._coerce_datetime(data.get("updated_at")),
        )

    def __repr__(self) -> str:
        return f"ClasseBase(id={self.id!r}, code={self.code!r}, libelle={self.libelle!r}, created_at={self.created_at!r}, updated_at={self.updated_at!r})"

