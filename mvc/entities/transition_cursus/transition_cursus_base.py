"""FICHIER GENERE PAR FORGE.
Base regenerable de l'entite TransitionCursus.
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


class TransitionCursusBase:
    """Classe de base regenerable de TransitionCursus."""

    def __init__(self, type_transition, formation_niveau_source_id, formation_niveau_cible_id, created_at, updated_at, id=None, conditions=None, date_debut_validite=None, date_fin_validite=None):
        self.type_transition = type_transition
        self.formation_niveau_source_id = formation_niveau_source_id
        self.formation_niveau_cible_id = formation_niveau_cible_id
        self.created_at = created_at
        self.updated_at = updated_at
        self.id = id
        self.conditions = conditions
        self.date_debut_validite = date_debut_validite
        self.date_fin_validite = date_fin_validite

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
    def type_transition(self):
        return self._type_transition

    @type_transition.setter
    @typed(str)
    def type_transition(self, value):
        if value is None:
            raise ValidationError("type_transition", 'La propriété "type_transition" ne peut pas être nulle.')
        self._type_transition = value

    @property
    def conditions(self):
        return self._conditions

    @conditions.setter
    @typed(str)
    @nullable
    def conditions(self, value):
        if value is None:
            self._conditions = None
            return
        self._conditions = value

    @property
    def date_debut_validite(self):
        return self._date_debut_validite

    @date_debut_validite.setter
    @typed(date)
    @nullable
    def date_debut_validite(self, value):
        if value is None:
            self._date_debut_validite = None
            return
        self._date_debut_validite = value

    @property
    def date_fin_validite(self):
        return self._date_fin_validite

    @date_fin_validite.setter
    @typed(date)
    @nullable
    def date_fin_validite(self, value):
        if value is None:
            self._date_fin_validite = None
            return
        self._date_fin_validite = value

    @property
    def formation_niveau_source_id(self):
        return self._formation_niveau_source_id

    @formation_niveau_source_id.setter
    @typed(int)
    def formation_niveau_source_id(self, value):
        if value is None:
            raise ValidationError("formation_niveau_source_id", 'La propriété "formation_niveau_source_id" ne peut pas être nulle.')
        self._formation_niveau_source_id = value

    @property
    def formation_niveau_cible_id(self):
        return self._formation_niveau_cible_id

    @formation_niveau_cible_id.setter
    @typed(int)
    def formation_niveau_cible_id(self, value):
        if value is None:
            raise ValidationError("formation_niveau_cible_id", 'La propriété "formation_niveau_cible_id" ne peut pas être nulle.')
        self._formation_niveau_cible_id = value

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
            "type_transition": self.type_transition,
            "conditions": self.conditions,
            "date_debut_validite": None if self.date_debut_validite is None else self.date_debut_validite.isoformat(),
            "date_fin_validite": None if self.date_fin_validite is None else self.date_fin_validite.isoformat(),
            "formation_niveau_source_id": self.formation_niveau_source_id,
            "formation_niveau_cible_id": self.formation_niveau_cible_id,
            "created_at": None if self.created_at is None else self.created_at.isoformat(),
            "updated_at": None if self.updated_at is None else self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TransitionCursusBase":
        return cls(
            id=data["id"],
            type_transition=data["type_transition"],
            conditions=data["conditions"],
            date_debut_validite=cls._coerce_date(data.get("date_debut_validite")),
            date_fin_validite=cls._coerce_date(data.get("date_fin_validite")),
            formation_niveau_source_id=data["formation_niveau_source_id"],
            formation_niveau_cible_id=data["formation_niveau_cible_id"],
            created_at=cls._coerce_datetime(data.get("created_at")),
            updated_at=cls._coerce_datetime(data.get("updated_at")),
        )

    def __repr__(self) -> str:
        return f"TransitionCursusBase(id={self.id!r}, type_transition={self.type_transition!r}, conditions={self.conditions!r}, date_debut_validite={self.date_debut_validite!r}, date_fin_validite={self.date_fin_validite!r}, formation_niveau_source_id={self.formation_niveau_source_id!r}, formation_niveau_cible_id={self.formation_niveau_cible_id!r}, created_at={self.created_at!r}, updated_at={self.updated_at!r})"

