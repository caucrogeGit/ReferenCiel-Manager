"""FICHIER GENERE PAR FORGE.
Base regenerable de l'entite Activite.
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


class ActiviteBase:
    """Classe de base regenerable de Activite."""

    def __init__(self, palier_id, created_at, updated_at, id=None, objectif=None, fichier=None):
        self.palier_id = palier_id
        self.created_at = created_at
        self.updated_at = updated_at
        self.id = id
        self.objectif = objectif
        self.fichier = fichier

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
    def objectif(self):
        return self._objectif

    @objectif.setter
    @typed(str)
    @nullable
    def objectif(self, value):
        if value is None:
            self._objectif = None
            return
        self._objectif = value

    @property
    def fichier(self):
        return self._fichier

    @fichier.setter
    @typed(str)
    @nullable
    def fichier(self, value):
        if value is None:
            self._fichier = None
            return
        self._fichier = value

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
            "objectif": self.objectif,
            "fichier": self.fichier,
            "palier_id": self.palier_id,
            "created_at": None if self.created_at is None else self.created_at.isoformat(),
            "updated_at": None if self.updated_at is None else self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ActiviteBase":
        return cls(
            id=data["id"],
            objectif=data["objectif"],
            fichier=data["fichier"],
            palier_id=data["palier_id"],
            created_at=cls._coerce_datetime(data.get("created_at")),
            updated_at=cls._coerce_datetime(data.get("updated_at")),
        )

    def __repr__(self) -> str:
        return f"ActiviteBase(id={self.id!r}, objectif={self.objectif!r}, fichier={self.fichier!r}, palier_id={self.palier_id!r}, created_at={self.created_at!r}, updated_at={self.updated_at!r})"

