"""FICHIER GENERE PAR FORGE.
Base regenerable de l'entite Source.
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


class SourceBase:
    """Classe de base regenerable de Source."""

    def __init__(self, source_id, source_type, source_fichier, referentiel_id, created_at, updated_at, id=None, source_note=None):
        self.source_id = source_id
        self.source_type = source_type
        self.source_fichier = source_fichier
        self.referentiel_id = referentiel_id
        self.created_at = created_at
        self.updated_at = updated_at
        self.id = id
        self.source_note = source_note

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
    def source_id(self):
        return self._source_id

    @source_id.setter
    @typed(str)
    def source_id(self, value):
        if value is None:
            raise ValidationError("source_id", 'La propriété "source_id" ne peut pas être nulle.')
        self._source_id = value

    @property
    def source_type(self):
        return self._source_type

    @source_type.setter
    @typed(str)
    def source_type(self, value):
        if value is None:
            raise ValidationError("source_type", 'La propriété "source_type" ne peut pas être nulle.')
        self._source_type = value

    @property
    def source_fichier(self):
        return self._source_fichier

    @source_fichier.setter
    @typed(str)
    def source_fichier(self, value):
        if value is None:
            raise ValidationError("source_fichier", 'La propriété "source_fichier" ne peut pas être nulle.')
        self._source_fichier = value

    @property
    def source_note(self):
        return self._source_note

    @source_note.setter
    @typed(str)
    @nullable
    def source_note(self, value):
        if value is None:
            self._source_note = None
            return
        self._source_note = value

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
            "source_id": self.source_id,
            "source_type": self.source_type,
            "source_fichier": self.source_fichier,
            "source_note": self.source_note,
            "referentiel_id": self.referentiel_id,
            "created_at": None if self.created_at is None else self.created_at.isoformat(),
            "updated_at": None if self.updated_at is None else self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SourceBase":
        return cls(
            id=data["id"],
            source_id=data["source_id"],
            source_type=data["source_type"],
            source_fichier=data["source_fichier"],
            source_note=data["source_note"],
            referentiel_id=data["referentiel_id"],
            created_at=cls._coerce_datetime(data.get("created_at")),
            updated_at=cls._coerce_datetime(data.get("updated_at")),
        )

    def __repr__(self) -> str:
        return f"SourceBase(id={self.id!r}, source_id={self.source_id!r}, source_type={self.source_type!r}, source_fichier={self.source_fichier!r}, source_note={self.source_note!r}, referentiel_id={self.referentiel_id!r}, created_at={self.created_at!r}, updated_at={self.updated_at!r})"

