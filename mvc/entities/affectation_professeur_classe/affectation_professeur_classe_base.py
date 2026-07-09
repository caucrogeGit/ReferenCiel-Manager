"""FICHIER GENERE PAR FORGE.
Base regenerable de l'entite AffectationProfesseurClasse.
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


class AffectationProfesseurClasseBase:
    """Classe de base regenerable de AffectationProfesseurClasse."""

    def __init__(self, professeur_id, classe_id, annee_scolaire_id, created_at, updated_at, id=None, role=None):
        self.professeur_id = professeur_id
        self.classe_id = classe_id
        self.annee_scolaire_id = annee_scolaire_id
        self.created_at = created_at
        self.updated_at = updated_at
        self.id = id
        self.role = role

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
    def role(self):
        return self._role

    @role.setter
    @typed(str)
    @nullable
    def role(self, value):
        if value is None:
            self._role = None
            return
        self._role = value

    @property
    def professeur_id(self):
        return self._professeur_id

    @professeur_id.setter
    @typed(int)
    def professeur_id(self, value):
        if value is None:
            raise ValidationError("professeur_id", 'La propriété "professeur_id" ne peut pas être nulle.')
        self._professeur_id = value

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
    def annee_scolaire_id(self):
        return self._annee_scolaire_id

    @annee_scolaire_id.setter
    @typed(int)
    def annee_scolaire_id(self, value):
        if value is None:
            raise ValidationError("annee_scolaire_id", 'La propriété "annee_scolaire_id" ne peut pas être nulle.')
        self._annee_scolaire_id = value

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
            "role": self.role,
            "professeur_id": self.professeur_id,
            "classe_id": self.classe_id,
            "annee_scolaire_id": self.annee_scolaire_id,
            "created_at": None if self.created_at is None else self.created_at.isoformat(),
            "updated_at": None if self.updated_at is None else self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AffectationProfesseurClasseBase":
        return cls(
            id=data["id"],
            role=data["role"],
            professeur_id=data["professeur_id"],
            classe_id=data["classe_id"],
            annee_scolaire_id=data["annee_scolaire_id"],
            created_at=cls._coerce_datetime(data.get("created_at")),
            updated_at=cls._coerce_datetime(data.get("updated_at")),
        )

    def __repr__(self) -> str:
        return f"AffectationProfesseurClasseBase(id={self.id!r}, role={self.role!r}, professeur_id={self.professeur_id!r}, classe_id={self.classe_id!r}, annee_scolaire_id={self.annee_scolaire_id!r}, created_at={self.created_at!r}, updated_at={self.updated_at!r})"

