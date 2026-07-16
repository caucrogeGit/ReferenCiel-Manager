"""FICHIER GENERE PAR FORGE.
Base regenerable de l'entite Seance.
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


class SeanceBase:
    """Classe de base regenerable de Seance."""

    def __init__(self, ordre, titre, sequence_id, created_at, updated_at, id=None, theme=None, production_attendue=None):
        self.ordre = ordre
        self.titre = titre
        self.sequence_id = sequence_id
        self.created_at = created_at
        self.updated_at = updated_at
        self.id = id
        self.theme = theme
        self.production_attendue = production_attendue

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
    def ordre(self):
        return self._ordre

    @ordre.setter
    @typed(int)
    def ordre(self, value):
        if value is None:
            raise ValidationError("ordre", 'La propriété "ordre" ne peut pas être nulle.')
        self._ordre = value

    @property
    def titre(self):
        return self._titre

    @titre.setter
    @typed(str)
    def titre(self, value):
        if value is None:
            raise ValidationError("titre", 'La propriété "titre" ne peut pas être nulle.')
        self._titre = value

    @property
    def theme(self):
        return self._theme

    @theme.setter
    @typed(str)
    @nullable
    def theme(self, value):
        if value is None:
            self._theme = None
            return
        self._theme = value

    @property
    def production_attendue(self):
        return self._production_attendue

    @production_attendue.setter
    @typed(str)
    @nullable
    def production_attendue(self, value):
        if value is None:
            self._production_attendue = None
            return
        self._production_attendue = value

    @property
    def sequence_id(self):
        return self._sequence_id

    @sequence_id.setter
    @typed(int)
    def sequence_id(self, value):
        if value is None:
            raise ValidationError("sequence_id", 'La propriété "sequence_id" ne peut pas être nulle.')
        self._sequence_id = value

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
            "ordre": self.ordre,
            "titre": self.titre,
            "theme": self.theme,
            "production_attendue": self.production_attendue,
            "sequence_id": self.sequence_id,
            "created_at": None if self.created_at is None else self.created_at.isoformat(),
            "updated_at": None if self.updated_at is None else self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SeanceBase":
        return cls(
            id=data["id"],
            ordre=data["ordre"],
            titre=data["titre"],
            theme=data["theme"],
            production_attendue=data["production_attendue"],
            sequence_id=data["sequence_id"],
            created_at=cls._coerce_datetime(data.get("created_at")),
            updated_at=cls._coerce_datetime(data.get("updated_at")),
        )

    def __repr__(self) -> str:
        return f"SeanceBase(id={self.id!r}, ordre={self.ordre!r}, titre={self.titre!r}, theme={self.theme!r}, production_attendue={self.production_attendue!r}, sequence_id={self.sequence_id!r}, created_at={self.created_at!r}, updated_at={self.updated_at!r})"

