"""FICHIER GENERE PAR FORGE.
Base regenerable de l'entite Groupe.
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


class GroupeBase:
    """Classe de base regenerable de Groupe."""

    def __init__(self, nom, classe_id, created_at, updated_at, id=None):
        self.nom = nom
        self.classe_id = classe_id
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
    def nom(self):
        return self._nom

    @nom.setter
    @typed(str)
    def nom(self, value):
        if value is None:
            raise ValidationError("nom", 'La propriété "nom" ne peut pas être nulle.')
        self._nom = value

    @property
    def classe_id(self):
        return self._classe_id

    @classe_id.setter
    @typed(int)
    def classe_id(self, value):
        if value is None:
            raise ValidationError("classe_id", 'La propriété "classe_id" ne peut pas être nulle.')
        self._classe_id = value

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
            "nom": self.nom,
            "classe_id": self.classe_id,
            "created_at": None if self.created_at is None else self.created_at.isoformat(),
            "updated_at": None if self.updated_at is None else self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "GroupeBase":
        return cls(
            id=data["id"],
            nom=data["nom"],
            classe_id=data["classe_id"],
            created_at=cls._coerce_datetime(data.get("created_at")),
            updated_at=cls._coerce_datetime(data.get("updated_at")),
        )

    def __repr__(self) -> str:
        return f"GroupeBase(id={self.id!r}, nom={self.nom!r}, classe_id={self.classe_id!r}, created_at={self.created_at!r}, updated_at={self.updated_at!r})"

