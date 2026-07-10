"""FICHIER GENERE PAR FORGE.
Base regenerable de l'entite AffectationParcours.
Ne pas y ajouter de logique metier manuelle.
"""

from __future__ import annotations

from typing import Any

from datetime import date, datetime

from core.validation import (
    ValidationError,
    nullable,
    typed,
)


class AffectationParcoursBase:
    """Classe de base regenerable de AffectationParcours."""

    def __init__(self, date_affectation, statut, version_parcours_id, classe_id, professeur_id, created_at, updated_at, id=None):
        self.date_affectation = date_affectation
        self.statut = statut
        self.version_parcours_id = version_parcours_id
        self.classe_id = classe_id
        self.professeur_id = professeur_id
        self.created_at = created_at
        self.updated_at = updated_at
        self.id = id

    @staticmethod
    def _coerce_date(value):
        if value is None or isinstance(value, date):
            return value
        return date.fromisoformat(value)

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
    def date_affectation(self):
        return self._date_affectation

    @date_affectation.setter
    @typed(date)
    def date_affectation(self, value):
        if value is None:
            raise ValidationError("date_affectation", 'La propriété "date_affectation" ne peut pas être nulle.')
        self._date_affectation = value

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
    def version_parcours_id(self):
        return self._version_parcours_id

    @version_parcours_id.setter
    @typed(int)
    def version_parcours_id(self, value):
        if value is None:
            raise ValidationError("version_parcours_id", 'La propriété "version_parcours_id" ne peut pas être nulle.')
        self._version_parcours_id = value

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
    def professeur_id(self):
        return self._professeur_id

    @professeur_id.setter
    @typed(int)
    def professeur_id(self, value):
        if value is None:
            raise ValidationError("professeur_id", 'La propriété "professeur_id" ne peut pas être nulle.')
        self._professeur_id = value

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
            "date_affectation": None if self.date_affectation is None else self.date_affectation.isoformat(),
            "statut": self.statut,
            "version_parcours_id": self.version_parcours_id,
            "classe_id": self.classe_id,
            "professeur_id": self.professeur_id,
            "created_at": None if self.created_at is None else self.created_at.isoformat(),
            "updated_at": None if self.updated_at is None else self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AffectationParcoursBase":
        return cls(
            id=data["id"],
            date_affectation=cls._coerce_date(data.get("date_affectation")),
            statut=data["statut"],
            version_parcours_id=data["version_parcours_id"],
            classe_id=data["classe_id"],
            professeur_id=data["professeur_id"],
            created_at=cls._coerce_datetime(data.get("created_at")),
            updated_at=cls._coerce_datetime(data.get("updated_at")),
        )

    def __repr__(self) -> str:
        return f"AffectationParcoursBase(id={self.id!r}, date_affectation={self.date_affectation!r}, statut={self.statut!r}, version_parcours_id={self.version_parcours_id!r}, classe_id={self.classe_id!r}, professeur_id={self.professeur_id!r}, created_at={self.created_at!r}, updated_at={self.updated_at!r})"

