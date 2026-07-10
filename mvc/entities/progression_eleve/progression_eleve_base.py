"""FICHIER GENERE PAR FORGE.
Base regenerable de l'entite ProgressionEleve.
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


class ProgressionEleveBase:
    """Classe de base regenerable de ProgressionEleve."""

    def __init__(self, statut, eleve_id, affectation_parcours_id, created_at, updated_at, id=None, date_debut=None):
        self.statut = statut
        self.eleve_id = eleve_id
        self.affectation_parcours_id = affectation_parcours_id
        self.created_at = created_at
        self.updated_at = updated_at
        self.id = id
        self.date_debut = date_debut

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
    def statut(self):
        return self._statut

    @statut.setter
    @typed(str)
    def statut(self, value):
        if value is None:
            raise ValidationError("statut", 'La propriété "statut" ne peut pas être nulle.')
        self._statut = value

    @property
    def date_debut(self):
        return self._date_debut

    @date_debut.setter
    @typed(date)
    @nullable
    def date_debut(self, value):
        if value is None:
            self._date_debut = None
            return
        self._date_debut = value

    @property
    def eleve_id(self):
        return self._eleve_id

    @eleve_id.setter
    @typed(int)
    def eleve_id(self, value):
        if value is None:
            raise ValidationError("eleve_id", 'La propriété "eleve_id" ne peut pas être nulle.')
        self._eleve_id = value

    @property
    def affectation_parcours_id(self):
        return self._affectation_parcours_id

    @affectation_parcours_id.setter
    @typed(int)
    def affectation_parcours_id(self, value):
        if value is None:
            raise ValidationError("affectation_parcours_id", 'La propriété "affectation_parcours_id" ne peut pas être nulle.')
        self._affectation_parcours_id = value

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
            "statut": self.statut,
            "date_debut": None if self.date_debut is None else self.date_debut.isoformat(),
            "eleve_id": self.eleve_id,
            "affectation_parcours_id": self.affectation_parcours_id,
            "created_at": None if self.created_at is None else self.created_at.isoformat(),
            "updated_at": None if self.updated_at is None else self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ProgressionEleveBase":
        return cls(
            id=data["id"],
            statut=data["statut"],
            date_debut=cls._coerce_date(data.get("date_debut")),
            eleve_id=data["eleve_id"],
            affectation_parcours_id=data["affectation_parcours_id"],
            created_at=cls._coerce_datetime(data.get("created_at")),
            updated_at=cls._coerce_datetime(data.get("updated_at")),
        )

    def __repr__(self) -> str:
        return f"ProgressionEleveBase(id={self.id!r}, statut={self.statut!r}, date_debut={self.date_debut!r}, eleve_id={self.eleve_id!r}, affectation_parcours_id={self.affectation_parcours_id!r}, created_at={self.created_at!r}, updated_at={self.updated_at!r})"

