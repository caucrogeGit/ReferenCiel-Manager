"""FICHIER GENERE PAR FORGE.
Base regenerable de l'entite Cursus.
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


class CursusBase:
    """Classe de base regenerable de Cursus."""

    def __init__(self, code, libelle, modalite, statut, certification_cible_id, created_at, updated_at, id=None, description=None):
        self.code = code
        self.libelle = libelle
        self.modalite = modalite
        self.statut = statut
        self.certification_cible_id = certification_cible_id
        self.created_at = created_at
        self.updated_at = updated_at
        self.id = id
        self.description = description

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
    def libelle(self, value):
        if value is None:
            raise ValidationError("libelle", 'La propriété "libelle" ne peut pas être nulle.')
        self._libelle = value

    @property
    def modalite(self):
        return self._modalite

    @modalite.setter
    @typed(str)
    def modalite(self, value):
        if value is None:
            raise ValidationError("modalite", 'La propriété "modalite" ne peut pas être nulle.')
        self._modalite = value

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
    def description(self):
        return self._description

    @description.setter
    @typed(str)
    @nullable
    def description(self, value):
        if value is None:
            self._description = None
            return
        self._description = value

    @property
    def certification_cible_id(self):
        return self._certification_cible_id

    @certification_cible_id.setter
    @typed(int)
    def certification_cible_id(self, value):
        if value is None:
            raise ValidationError("certification_cible_id", 'La propriété "certification_cible_id" ne peut pas être nulle.')
        self._certification_cible_id = value

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
            "modalite": self.modalite,
            "statut": self.statut,
            "description": self.description,
            "certification_cible_id": self.certification_cible_id,
            "created_at": None if self.created_at is None else self.created_at.isoformat(),
            "updated_at": None if self.updated_at is None else self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CursusBase":
        return cls(
            id=data["id"],
            code=data["code"],
            libelle=data["libelle"],
            modalite=data["modalite"],
            statut=data["statut"],
            description=data["description"],
            certification_cible_id=data["certification_cible_id"],
            created_at=cls._coerce_datetime(data.get("created_at")),
            updated_at=cls._coerce_datetime(data.get("updated_at")),
        )

    def __repr__(self) -> str:
        return f"CursusBase(id={self.id!r}, code={self.code!r}, libelle={self.libelle!r}, modalite={self.modalite!r}, statut={self.statut!r}, description={self.description!r}, certification_cible_id={self.certification_cible_id!r}, created_at={self.created_at!r}, updated_at={self.updated_at!r})"

