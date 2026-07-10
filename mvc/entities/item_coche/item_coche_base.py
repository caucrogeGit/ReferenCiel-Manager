"""FICHIER GENERE PAR FORGE.
Base regenerable de l'entite ItemCoche.
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


class ItemCocheBase:
    """Classe de base regenerable de ItemCoche."""

    def __init__(self, coche_eleve, coche_professeur, item_id, progression_palier_id, created_at, updated_at, id=None):
        self.coche_eleve = coche_eleve
        self.coche_professeur = coche_professeur
        self.item_id = item_id
        self.progression_palier_id = progression_palier_id
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
    def coche_eleve(self):
        return self._coche_eleve

    @coche_eleve.setter
    @typed(bool)
    def coche_eleve(self, value):
        if value is None:
            raise ValidationError("coche_eleve", 'La propriété "coche_eleve" ne peut pas être nulle.')
        self._coche_eleve = value

    @property
    def coche_professeur(self):
        return self._coche_professeur

    @coche_professeur.setter
    @typed(bool)
    def coche_professeur(self, value):
        if value is None:
            raise ValidationError("coche_professeur", 'La propriété "coche_professeur" ne peut pas être nulle.')
        self._coche_professeur = value

    @property
    def item_id(self):
        return self._item_id

    @item_id.setter
    @typed(int)
    def item_id(self, value):
        if value is None:
            raise ValidationError("item_id", 'La propriété "item_id" ne peut pas être nulle.')
        self._item_id = value

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
            "coche_eleve": self.coche_eleve,
            "coche_professeur": self.coche_professeur,
            "item_id": self.item_id,
            "progression_palier_id": self.progression_palier_id,
            "created_at": None if self.created_at is None else self.created_at.isoformat(),
            "updated_at": None if self.updated_at is None else self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ItemCocheBase":
        return cls(
            id=data["id"],
            coche_eleve=data["coche_eleve"],
            coche_professeur=data["coche_professeur"],
            item_id=data["item_id"],
            progression_palier_id=data["progression_palier_id"],
            created_at=cls._coerce_datetime(data.get("created_at")),
            updated_at=cls._coerce_datetime(data.get("updated_at")),
        )

    def __repr__(self) -> str:
        return f"ItemCocheBase(id={self.id!r}, coche_eleve={self.coche_eleve!r}, coche_professeur={self.coche_professeur!r}, item_id={self.item_id!r}, progression_palier_id={self.progression_palier_id!r}, created_at={self.created_at!r}, updated_at={self.updated_at!r})"

