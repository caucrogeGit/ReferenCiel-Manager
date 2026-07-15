"""FICHIER GENERE PAR FORGE.
Base regenerable de l'entite RelationFormation.
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


class RelationFormationBase:
    """Classe de base regenerable de RelationFormation."""

    def __init__(self, type_relation, formation_source_id, formation_cible_id, created_at, updated_at, id=None):
        self.type_relation = type_relation
        self.formation_source_id = formation_source_id
        self.formation_cible_id = formation_cible_id
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
    def type_relation(self):
        return self._type_relation

    @type_relation.setter
    @typed(str)
    def type_relation(self, value):
        if value is None:
            raise ValidationError("type_relation", 'La propriété "type_relation" ne peut pas être nulle.')
        self._type_relation = value

    @property
    def formation_source_id(self):
        return self._formation_source_id

    @formation_source_id.setter
    @typed(int)
    def formation_source_id(self, value):
        if value is None:
            raise ValidationError("formation_source_id", 'La propriété "formation_source_id" ne peut pas être nulle.')
        self._formation_source_id = value

    @property
    def formation_cible_id(self):
        return self._formation_cible_id

    @formation_cible_id.setter
    @typed(int)
    def formation_cible_id(self, value):
        if value is None:
            raise ValidationError("formation_cible_id", 'La propriété "formation_cible_id" ne peut pas être nulle.')
        self._formation_cible_id = value

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
            "type_relation": self.type_relation,
            "formation_source_id": self.formation_source_id,
            "formation_cible_id": self.formation_cible_id,
            "created_at": None if self.created_at is None else self.created_at.isoformat(),
            "updated_at": None if self.updated_at is None else self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RelationFormationBase":
        return cls(
            id=data["id"],
            type_relation=data["type_relation"],
            formation_source_id=data["formation_source_id"],
            formation_cible_id=data["formation_cible_id"],
            created_at=cls._coerce_datetime(data.get("created_at")),
            updated_at=cls._coerce_datetime(data.get("updated_at")),
        )

    def __repr__(self) -> str:
        return f"RelationFormationBase(id={self.id!r}, type_relation={self.type_relation!r}, formation_source_id={self.formation_source_id!r}, formation_cible_id={self.formation_cible_id!r}, created_at={self.created_at!r}, updated_at={self.updated_at!r})"

