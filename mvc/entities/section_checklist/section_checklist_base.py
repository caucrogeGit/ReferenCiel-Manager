"""FICHIER GENERE PAR FORGE.
Base regenerable de l'entite SectionChecklist.
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


class SectionChecklistBase:
    """Classe de base regenerable de SectionChecklist."""

    def __init__(self, numero, titre, checklist_id, created_at, updated_at, id=None):
        self.numero = numero
        self.titre = titre
        self.checklist_id = checklist_id
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
    def numero(self):
        return self._numero

    @numero.setter
    @typed(int)
    def numero(self, value):
        if value is None:
            raise ValidationError("numero", 'La propriété "numero" ne peut pas être nulle.')
        self._numero = value

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
    def checklist_id(self):
        return self._checklist_id

    @checklist_id.setter
    @typed(int)
    def checklist_id(self, value):
        if value is None:
            raise ValidationError("checklist_id", 'La propriété "checklist_id" ne peut pas être nulle.')
        self._checklist_id = value

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
            "numero": self.numero,
            "titre": self.titre,
            "checklist_id": self.checklist_id,
            "created_at": None if self.created_at is None else self.created_at.isoformat(),
            "updated_at": None if self.updated_at is None else self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SectionChecklistBase":
        return cls(
            id=data["id"],
            numero=data["numero"],
            titre=data["titre"],
            checklist_id=data["checklist_id"],
            created_at=cls._coerce_datetime(data.get("created_at")),
            updated_at=cls._coerce_datetime(data.get("updated_at")),
        )

    def __repr__(self) -> str:
        return f"SectionChecklistBase(id={self.id!r}, numero={self.numero!r}, titre={self.titre!r}, checklist_id={self.checklist_id!r}, created_at={self.created_at!r}, updated_at={self.updated_at!r})"

