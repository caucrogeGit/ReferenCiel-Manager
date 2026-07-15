"""FICHIER GENERE PAR FORGE.
Base regenerable de l'entite ReferentielNiveauClasse.
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


class ReferentielNiveauClasseBase:
    """Classe de base regenerable de ReferentielNiveauClasse."""

    def __init__(self, identifiant, version, statut, importe_le, formation_id, created_at, updated_at, id=None):
        self.identifiant = identifiant
        self.version = version
        self.statut = statut
        self.importe_le = importe_le
        self.formation_id = formation_id
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
    def identifiant(self):
        return self._identifiant

    @identifiant.setter
    @typed(str)
    def identifiant(self, value):
        if value is None:
            raise ValidationError("identifiant", 'La propriété "identifiant" ne peut pas être nulle.')
        self._identifiant = value

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
    def importe_le(self):
        return self._importe_le

    @importe_le.setter
    @typed(datetime)
    def importe_le(self, value):
        if value is None:
            raise ValidationError("importe_le", 'La propriété "importe_le" ne peut pas être nulle.')
        self._importe_le = value

    @property
    def formation_id(self):
        return self._formation_id

    @formation_id.setter
    @typed(int)
    def formation_id(self, value):
        if value is None:
            raise ValidationError("formation_id", 'La propriété "formation_id" ne peut pas être nulle.')
        self._formation_id = value

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
            "identifiant": self.identifiant,
            "version": self.version,
            "statut": self.statut,
            "importe_le": None if self.importe_le is None else self.importe_le.isoformat(),
            "formation_id": self.formation_id,
            "created_at": None if self.created_at is None else self.created_at.isoformat(),
            "updated_at": None if self.updated_at is None else self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ReferentielNiveauClasseBase":
        return cls(
            id=data["id"],
            identifiant=data["identifiant"],
            version=data["version"],
            statut=data["statut"],
            importe_le=cls._coerce_datetime(data.get("importe_le")),
            formation_id=data["formation_id"],
            created_at=cls._coerce_datetime(data.get("created_at")),
            updated_at=cls._coerce_datetime(data.get("updated_at")),
        )

    def __repr__(self) -> str:
        return f"ReferentielNiveauClasseBase(id={self.id!r}, identifiant={self.identifiant!r}, version={self.version!r}, statut={self.statut!r}, importe_le={self.importe_le!r}, formation_id={self.formation_id!r}, created_at={self.created_at!r}, updated_at={self.updated_at!r})"

