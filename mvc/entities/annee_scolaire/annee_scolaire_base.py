"""FICHIER GENERE PAR FORGE.
Base regenerable de l'entite AnneeScolaire.
Ne pas y ajouter de logique metier manuelle.
"""

from __future__ import annotations

from datetime import date, datetime

from core.validation import (
    ValidationError,
    nullable,
    typed,
)


class AnneeScolaireBase:
    """Classe de base regenerable de AnneeScolaire."""

    def __init__(self, libelle, created_at, updated_at, id=None, date_debut=None, date_fin=None, active=False):
        self.libelle = libelle
        self.created_at = created_at
        self.updated_at = updated_at
        self.id = id
        self.date_debut = date_debut
        self.date_fin = date_fin
        self.active = active

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
    def libelle(self):
        return self._libelle

    @libelle.setter
    @typed(str)
    def libelle(self, value):
        if value is None:
            raise ValidationError("libelle", 'La propriété "libelle" ne peut pas être nulle.')
        self._libelle = value

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
    def date_fin(self):
        return self._date_fin

    @date_fin.setter
    @typed(date)
    @nullable
    def date_fin(self, value):
        if value is None:
            self._date_fin = None
            return
        self._date_fin = value

    @property
    def active(self):
        return self._active

    @active.setter
    @typed(bool)
    def active(self, value):
        if value is None:
            raise ValidationError("active", 'La propriété "active" ne peut pas être nulle.')
        self._active = value

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
            "libelle": self.libelle,
            "date_debut": None if self.date_debut is None else self.date_debut.isoformat(),
            "date_fin": None if self.date_fin is None else self.date_fin.isoformat(),
            "active": self.active,
            "created_at": None if self.created_at is None else self.created_at.isoformat(),
            "updated_at": None if self.updated_at is None else self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AnneeScolaireBase":
        return cls(
            id=data.get("id"),
            libelle=data.get("libelle"),
            date_debut=cls._coerce_date(data.get("date_debut")),
            date_fin=cls._coerce_date(data.get("date_fin")),
            active=data.get("active"),
            created_at=cls._coerce_datetime(data.get("created_at")),
            updated_at=cls._coerce_datetime(data.get("updated_at")),
        )

    def __repr__(self) -> str:
        return f"AnneeScolaireBase(id={self.id!r}, libelle={self.libelle!r}, date_debut={self.date_debut!r}, date_fin={self.date_fin!r}, active={self.active!r}, created_at={self.created_at!r}, updated_at={self.updated_at!r})"

