"""FICHIER GENERE PAR FORGE.
Base regenerable de l'entite BilanEleve.
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


class BilanEleveBase:
    """Classe de base regenerable de BilanEleve."""

    def __init__(self, appreciation_globale, statut, date_bilan, eleve_id, professeur_id, progression_parcours_id, created_at, updated_at, id=None, synthese=None):
        self.appreciation_globale = appreciation_globale
        self.statut = statut
        self.date_bilan = date_bilan
        self.eleve_id = eleve_id
        self.professeur_id = professeur_id
        self.progression_parcours_id = progression_parcours_id
        self.created_at = created_at
        self.updated_at = updated_at
        self.id = id
        self.synthese = synthese

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
    def appreciation_globale(self):
        return self._appreciation_globale

    @appreciation_globale.setter
    @typed(str)
    def appreciation_globale(self, value):
        if value is None:
            raise ValidationError("appreciation_globale", 'La propriété "appreciation_globale" ne peut pas être nulle.')
        self._appreciation_globale = value

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
    def date_bilan(self):
        return self._date_bilan

    @date_bilan.setter
    @typed(datetime)
    def date_bilan(self, value):
        if value is None:
            raise ValidationError("date_bilan", 'La propriété "date_bilan" ne peut pas être nulle.')
        self._date_bilan = value

    @property
    def synthese(self):
        return self._synthese

    @synthese.setter
    @typed(str)
    @nullable
    def synthese(self, value):
        if value is None:
            self._synthese = None
            return
        self._synthese = value

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
    def professeur_id(self):
        return self._professeur_id

    @professeur_id.setter
    @typed(int)
    def professeur_id(self, value):
        if value is None:
            raise ValidationError("professeur_id", 'La propriété "professeur_id" ne peut pas être nulle.')
        self._professeur_id = value

    @property
    def progression_parcours_id(self):
        return self._progression_parcours_id

    @progression_parcours_id.setter
    @typed(int)
    def progression_parcours_id(self, value):
        if value is None:
            raise ValidationError("progression_parcours_id", 'La propriété "progression_parcours_id" ne peut pas être nulle.')
        self._progression_parcours_id = value

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
            "appreciation_globale": self.appreciation_globale,
            "statut": self.statut,
            "date_bilan": None if self.date_bilan is None else self.date_bilan.isoformat(),
            "synthese": self.synthese,
            "eleve_id": self.eleve_id,
            "professeur_id": self.professeur_id,
            "progression_parcours_id": self.progression_parcours_id,
            "created_at": None if self.created_at is None else self.created_at.isoformat(),
            "updated_at": None if self.updated_at is None else self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BilanEleveBase":
        return cls(
            id=data["id"],
            appreciation_globale=data["appreciation_globale"],
            statut=data["statut"],
            date_bilan=cls._coerce_datetime(data.get("date_bilan")),
            synthese=data["synthese"],
            eleve_id=data["eleve_id"],
            professeur_id=data["professeur_id"],
            progression_parcours_id=data["progression_parcours_id"],
            created_at=cls._coerce_datetime(data.get("created_at")),
            updated_at=cls._coerce_datetime(data.get("updated_at")),
        )

    def __repr__(self) -> str:
        return f"BilanEleveBase(id={self.id!r}, appreciation_globale={self.appreciation_globale!r}, statut={self.statut!r}, date_bilan={self.date_bilan!r}, synthese={self.synthese!r}, eleve_id={self.eleve_id!r}, professeur_id={self.professeur_id!r}, progression_parcours_id={self.progression_parcours_id!r}, created_at={self.created_at!r}, updated_at={self.updated_at!r})"

