"""FICHIER GENERE PAR FORGE.
Base regenerable de l'entite Tache.
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


class TacheBase:
    """Classe de base regenerable de Tache."""

    def __init__(self, ordre, libelle, activite_id, created_at, updated_at, id=None):
        self.ordre = ordre
        self.libelle = libelle
        self.activite_id = activite_id
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
    def ordre(self):
        return self._ordre

    @ordre.setter
    @typed(int)
    def ordre(self, value):
        if value is None:
            raise ValidationError("ordre", 'La propriété "ordre" ne peut pas être nulle.')
        self._ordre = value

    @property
    def libelle(self):
        return self._libelle

    @libelle.setter
    @typed(str)
    def libelle(self, value):
        if value is None:
            raise ValidationError("libelle", 'La propriété "libelle" ne peut pas être nulle.')
        self._libelle = value

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
            "ordre": self.ordre,
            "libelle": self.libelle,
            "activite_id": self.activite_id,
            "created_at": None if self.created_at is None else self.created_at.isoformat(),
            "updated_at": None if self.updated_at is None else self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TacheBase":
        return cls(
            id=data["id"],
            ordre=data["ordre"],
            libelle=data["libelle"],
            activite_id=data["activite_id"],
            created_at=cls._coerce_datetime(data.get("created_at")),
            updated_at=cls._coerce_datetime(data.get("updated_at")),
        )

    def __repr__(self) -> str:
        return f"TacheBase(id={self.id!r}, ordre={self.ordre!r}, libelle={self.libelle!r}, activite_id={self.activite_id!r}, created_at={self.created_at!r}, updated_at={self.updated_at!r})"

