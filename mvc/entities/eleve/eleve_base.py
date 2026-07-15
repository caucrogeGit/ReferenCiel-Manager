"""FICHIER GENERE PAR FORGE.
Base regenerable de l'entite Eleve.
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


class EleveBase:
    """Classe de base regenerable de Eleve."""

    def __init__(self, nom, prenom, classe_id, created_at, updated_at, id=None, identifiant=None, date_naissance=None, user_id=None):
        self.nom = nom
        self.prenom = prenom
        self.classe_id = classe_id
        self.created_at = created_at
        self.updated_at = updated_at
        self.id = id
        self.identifiant = identifiant
        self.date_naissance = date_naissance
        self.user_id = user_id

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
    def nom(self):
        return self._nom

    @nom.setter
    @typed(str)
    def nom(self, value):
        if value is None:
            raise ValidationError("nom", 'La propriété "nom" ne peut pas être nulle.')
        self._nom = value

    @property
    def prenom(self):
        return self._prenom

    @prenom.setter
    @typed(str)
    def prenom(self, value):
        if value is None:
            raise ValidationError("prenom", 'La propriété "prenom" ne peut pas être nulle.')
        self._prenom = value

    @property
    def identifiant(self):
        return self._identifiant

    @identifiant.setter
    @typed(str)
    @nullable
    def identifiant(self, value):
        if value is None:
            self._identifiant = None
            return
        self._identifiant = value

    @property
    def date_naissance(self):
        return self._date_naissance

    @date_naissance.setter
    @typed(date)
    @nullable
    def date_naissance(self, value):
        if value is None:
            self._date_naissance = None
            return
        self._date_naissance = value

    @property
    def user_id(self):
        return self._user_id

    @user_id.setter
    @typed(int)
    @nullable
    def user_id(self, value):
        if value is None:
            self._user_id = None
            return
        self._user_id = value

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
            "prenom": self.prenom,
            "identifiant": self.identifiant,
            "date_naissance": None if self.date_naissance is None else self.date_naissance.isoformat(),
            "user_id": self.user_id,
            "classe_id": self.classe_id,
            "created_at": None if self.created_at is None else self.created_at.isoformat(),
            "updated_at": None if self.updated_at is None else self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EleveBase":
        return cls(
            id=data["id"],
            nom=data["nom"],
            prenom=data["prenom"],
            identifiant=data["identifiant"],
            date_naissance=cls._coerce_date(data.get("date_naissance")),
            user_id=data["user_id"],
            classe_id=data["classe_id"],
            created_at=cls._coerce_datetime(data.get("created_at")),
            updated_at=cls._coerce_datetime(data.get("updated_at")),
        )

    def __repr__(self) -> str:
        return f"EleveBase(id={self.id!r}, nom={self.nom!r}, prenom={self.prenom!r}, identifiant={self.identifiant!r}, date_naissance={self.date_naissance!r}, user_id={self.user_id!r}, classe_id={self.classe_id!r}, created_at={self.created_at!r}, updated_at={self.updated_at!r})"

