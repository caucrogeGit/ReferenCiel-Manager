"""FICHIER GENERE PAR FORGE.
Base regenerable de l'entite DepotEleve.
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


class DepotEleveBase:
    """Classe de base regenerable de DepotEleve."""

    def __init__(self, fichier, date_depot, progression_palier_id, activite_id, created_at, updated_at, id=None, commentaire=None):
        self.fichier = fichier
        self.date_depot = date_depot
        self.progression_palier_id = progression_palier_id
        self.activite_id = activite_id
        self.created_at = created_at
        self.updated_at = updated_at
        self.id = id
        self.commentaire = commentaire

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
    def fichier(self):
        return self._fichier

    @fichier.setter
    @typed(str)
    def fichier(self, value):
        if value is None:
            raise ValidationError("fichier", 'La propriété "fichier" ne peut pas être nulle.')
        self._fichier = value

    @property
    def commentaire(self):
        return self._commentaire

    @commentaire.setter
    @typed(str)
    @nullable
    def commentaire(self, value):
        if value is None:
            self._commentaire = None
            return
        self._commentaire = value

    @property
    def date_depot(self):
        return self._date_depot

    @date_depot.setter
    @typed(datetime)
    def date_depot(self, value):
        if value is None:
            raise ValidationError("date_depot", 'La propriété "date_depot" ne peut pas être nulle.')
        self._date_depot = value

    @property
    def progression_palier_id(self):
        return self._progression_palier_id

    @progression_palier_id.setter
    @typed(int)
    def progression_palier_id(self, value):
        if value is None:
            raise ValidationError("progression_palier_id", 'La propriété "progression_palier_id" ne peut pas être nulle.')
        self._progression_palier_id = value

    @property
    def activite_id(self):
        return self._activite_id

    @activite_id.setter
    @typed(int)
    def activite_id(self, value):
        if value is None:
            raise ValidationError("activite_id", 'La propriété "activite_id" ne peut pas être nulle.')
        self._activite_id = value

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
            "fichier": self.fichier,
            "commentaire": self.commentaire,
            "date_depot": None if self.date_depot is None else self.date_depot.isoformat(),
            "progression_palier_id": self.progression_palier_id,
            "activite_id": self.activite_id,
            "created_at": None if self.created_at is None else self.created_at.isoformat(),
            "updated_at": None if self.updated_at is None else self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DepotEleveBase":
        return cls(
            id=data["id"],
            fichier=data["fichier"],
            commentaire=data["commentaire"],
            date_depot=cls._coerce_datetime(data.get("date_depot")),
            progression_palier_id=data["progression_palier_id"],
            activite_id=data["activite_id"],
            created_at=cls._coerce_datetime(data.get("created_at")),
            updated_at=cls._coerce_datetime(data.get("updated_at")),
        )

    def __repr__(self) -> str:
        return f"DepotEleveBase(id={self.id!r}, fichier={self.fichier!r}, commentaire={self.commentaire!r}, date_depot={self.date_depot!r}, progression_palier_id={self.progression_palier_id!r}, activite_id={self.activite_id!r}, created_at={self.created_at!r}, updated_at={self.updated_at!r})"

