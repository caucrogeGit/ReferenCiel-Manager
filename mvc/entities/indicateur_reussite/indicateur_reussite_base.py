"""FICHIER GENERE PAR FORGE.
Base regenerable de l'entite IndicateurReussite.
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


class IndicateurReussiteBase:
    """Classe de base regenerable de IndicateurReussite."""

    def __init__(self, code, libelle, origine, referentiel_id, created_at, updated_at, id=None, ref_code=None):
        self.code = code
        self.libelle = libelle
        self.origine = origine
        self.referentiel_id = referentiel_id
        self.created_at = created_at
        self.updated_at = updated_at
        self.id = id
        self.ref_code = ref_code

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
    def code(self):
        return self._code

    @code.setter
    @typed(str)
    def code(self, value):
        if value is None:
            raise ValidationError("code", 'La propriété "code" ne peut pas être nulle.')
        self._code = value

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
    def origine(self):
        return self._origine

    @origine.setter
    @typed(str)
    def origine(self, value):
        if value is None:
            raise ValidationError("origine", 'La propriété "origine" ne peut pas être nulle.')
        self._origine = value

    @property
    def ref_code(self):
        return self._ref_code

    @ref_code.setter
    @typed(str)
    @nullable
    def ref_code(self, value):
        if value is None:
            self._ref_code = None
            return
        self._ref_code = value

    @property
    def referentiel_id(self):
        return self._referentiel_id

    @referentiel_id.setter
    @typed(int)
    def referentiel_id(self, value):
        if value is None:
            raise ValidationError("referentiel_id", 'La propriété "referentiel_id" ne peut pas être nulle.')
        self._referentiel_id = value

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
            "code": self.code,
            "libelle": self.libelle,
            "origine": self.origine,
            "ref_code": self.ref_code,
            "referentiel_id": self.referentiel_id,
            "created_at": None if self.created_at is None else self.created_at.isoformat(),
            "updated_at": None if self.updated_at is None else self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "IndicateurReussiteBase":
        return cls(
            id=data["id"],
            code=data["code"],
            libelle=data["libelle"],
            origine=data["origine"],
            ref_code=data["ref_code"],
            referentiel_id=data["referentiel_id"],
            created_at=cls._coerce_datetime(data.get("created_at")),
            updated_at=cls._coerce_datetime(data.get("updated_at")),
        )

    def __repr__(self) -> str:
        return f"IndicateurReussiteBase(id={self.id!r}, code={self.code!r}, libelle={self.libelle!r}, origine={self.origine!r}, ref_code={self.ref_code!r}, referentiel_id={self.referentiel_id!r}, created_at={self.created_at!r}, updated_at={self.updated_at!r})"

