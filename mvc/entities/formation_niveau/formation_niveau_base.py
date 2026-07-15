"""FICHIER GENERE PAR FORGE.
Base regenerable de l'entite FormationNiveau.
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


class FormationNiveauBase:
    """Classe de base regenerable de FormationNiveau."""

    def __init__(self, code, libelle, ordre_indicatif, formation_id, niveau_classe_id, created_at, updated_at, id=None):
        self.code = code
        self.libelle = libelle
        self.ordre_indicatif = ordre_indicatif
        self.formation_id = formation_id
        self.niveau_classe_id = niveau_classe_id
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
    def ordre_indicatif(self):
        return self._ordre_indicatif

    @ordre_indicatif.setter
    @typed(int)
    def ordre_indicatif(self, value):
        if value is None:
            raise ValidationError("ordre_indicatif", 'La propriété "ordre_indicatif" ne peut pas être nulle.')
        self._ordre_indicatif = value

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
    def niveau_classe_id(self):
        return self._niveau_classe_id

    @niveau_classe_id.setter
    @typed(int)
    def niveau_classe_id(self, value):
        if value is None:
            raise ValidationError("niveau_classe_id", 'La propriété "niveau_classe_id" ne peut pas être nulle.')
        self._niveau_classe_id = value

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
            "ordre_indicatif": self.ordre_indicatif,
            "formation_id": self.formation_id,
            "niveau_classe_id": self.niveau_classe_id,
            "created_at": None if self.created_at is None else self.created_at.isoformat(),
            "updated_at": None if self.updated_at is None else self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "FormationNiveauBase":
        return cls(
            id=data["id"],
            code=data["code"],
            libelle=data["libelle"],
            ordre_indicatif=data["ordre_indicatif"],
            formation_id=data["formation_id"],
            niveau_classe_id=data["niveau_classe_id"],
            created_at=cls._coerce_datetime(data.get("created_at")),
            updated_at=cls._coerce_datetime(data.get("updated_at")),
        )

    def __repr__(self) -> str:
        return f"FormationNiveauBase(id={self.id!r}, code={self.code!r}, libelle={self.libelle!r}, ordre_indicatif={self.ordre_indicatif!r}, formation_id={self.formation_id!r}, niveau_classe_id={self.niveau_classe_id!r}, created_at={self.created_at!r}, updated_at={self.updated_at!r})"

