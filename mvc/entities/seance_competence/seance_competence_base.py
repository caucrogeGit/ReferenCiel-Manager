"""FICHIER GENERE PAR FORGE.
Base regenerable de l'entite SeanceCompetence.
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


class SeanceCompetenceBase:
    """Classe de base regenerable de SeanceCompetence."""

    def __init__(self, seance_id, competence_id, role, created_at, updated_at, id=None):
        self.seance_id = seance_id
        self.competence_id = competence_id
        self.role = role
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
    def seance_id(self):
        return self._seance_id

    @seance_id.setter
    @typed(int)
    def seance_id(self, value):
        if value is None:
            raise ValidationError("seance_id", 'La propriété "seance_id" ne peut pas être nulle.')
        self._seance_id = value

    @property
    def competence_id(self):
        return self._competence_id

    @competence_id.setter
    @typed(int)
    def competence_id(self, value):
        if value is None:
            raise ValidationError("competence_id", 'La propriété "competence_id" ne peut pas être nulle.')
        self._competence_id = value

    @property
    def role(self):
        return self._role

    @role.setter
    @typed(str)
    def role(self, value):
        if value is None:
            raise ValidationError("role", 'La propriété "role" ne peut pas être nulle.')
        self._role = value

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
            "seance_id": self.seance_id,
            "competence_id": self.competence_id,
            "role": self.role,
            "created_at": None if self.created_at is None else self.created_at.isoformat(),
            "updated_at": None if self.updated_at is None else self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SeanceCompetenceBase":
        return cls(
            id=data["id"],
            seance_id=data["seance_id"],
            competence_id=data["competence_id"],
            role=data["role"],
            created_at=cls._coerce_datetime(data.get("created_at")),
            updated_at=cls._coerce_datetime(data.get("updated_at")),
        )

    def __repr__(self) -> str:
        return f"SeanceCompetenceBase(id={self.id!r}, seance_id={self.seance_id!r}, competence_id={self.competence_id!r}, role={self.role!r}, created_at={self.created_at!r}, updated_at={self.updated_at!r})"

