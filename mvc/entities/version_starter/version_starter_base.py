"""FICHIER GENERE PAR FORGE.
Base regenerable de l'entite VersionStarter.
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


class VersionStarterBase:
    """Classe de base regenerable de VersionStarter."""

    def __init__(self, version, statut, activite_glissante, ordre_impose, starter_id, created_at, updated_at, id=None):
        self.version = version
        self.statut = statut
        self.activite_glissante = activite_glissante
        self.ordre_impose = ordre_impose
        self.starter_id = starter_id
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
    def version(self):
        return self._version

    @version.setter
    @typed(str)
    def version(self, value):
        if value is None:
            raise ValidationError("version", 'La propriété "version" ne peut pas être nulle.')
        self._version = value

    @property
    def statut(self):
        return self._statut

    @statut.setter
    @typed(str)
    def statut(self, value):
        if value is None:
            raise ValidationError("statut", 'La propriété "statut" ne peut pas être nulle.')
        self._statut = value

    @property
    def activite_glissante(self):
        return self._activite_glissante

    @activite_glissante.setter
    @typed(bool)
    def activite_glissante(self, value):
        if value is None:
            raise ValidationError("activite_glissante", 'La propriété "activite_glissante" ne peut pas être nulle.')
        self._activite_glissante = value

    @property
    def ordre_impose(self):
        return self._ordre_impose

    @ordre_impose.setter
    @typed(bool)
    def ordre_impose(self, value):
        if value is None:
            raise ValidationError("ordre_impose", 'La propriété "ordre_impose" ne peut pas être nulle.')
        self._ordre_impose = value

    @property
    def starter_id(self):
        return self._starter_id

    @starter_id.setter
    @typed(int)
    def starter_id(self, value):
        if value is None:
            raise ValidationError("starter_id", 'La propriété "starter_id" ne peut pas être nulle.')
        self._starter_id = value

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
            "version": self.version,
            "statut": self.statut,
            "activite_glissante": self.activite_glissante,
            "ordre_impose": self.ordre_impose,
            "starter_id": self.starter_id,
            "created_at": None if self.created_at is None else self.created_at.isoformat(),
            "updated_at": None if self.updated_at is None else self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "VersionStarterBase":
        return cls(
            id=data["id"],
            version=data["version"],
            statut=data["statut"],
            activite_glissante=data["activite_glissante"],
            ordre_impose=data["ordre_impose"],
            starter_id=data["starter_id"],
            created_at=cls._coerce_datetime(data.get("created_at")),
            updated_at=cls._coerce_datetime(data.get("updated_at")),
        )

    def __repr__(self) -> str:
        return f"VersionStarterBase(id={self.id!r}, version={self.version!r}, statut={self.statut!r}, activite_glissante={self.activite_glissante!r}, ordre_impose={self.ordre_impose!r}, starter_id={self.starter_id!r}, created_at={self.created_at!r}, updated_at={self.updated_at!r})"

