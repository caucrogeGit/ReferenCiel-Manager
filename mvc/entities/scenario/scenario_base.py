"""FICHIER GENERE PAR FORGE.
Base regenerable de l'entite Scenario.
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


class ScenarioBase:
    """Classe de base regenerable de Scenario."""

    def __init__(self, titre, intention, statut, version, referentiel_id, auteur_id, created_at, updated_at, id=None, objectifs=None):
        self.titre = titre
        self.intention = intention
        self.statut = statut
        self.version = version
        self.referentiel_id = referentiel_id
        self.auteur_id = auteur_id
        self.created_at = created_at
        self.updated_at = updated_at
        self.id = id
        self.objectifs = objectifs

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
    def titre(self):
        return self._titre

    @titre.setter
    @typed(str)
    def titre(self, value):
        if value is None:
            raise ValidationError("titre", 'La propriété "titre" ne peut pas être nulle.')
        self._titre = value

    @property
    def intention(self):
        return self._intention

    @intention.setter
    @typed(str)
    def intention(self, value):
        if value is None:
            raise ValidationError("intention", 'La propriété "intention" ne peut pas être nulle.')
        self._intention = value

    @property
    def objectifs(self):
        return self._objectifs

    @objectifs.setter
    @typed(str)
    @nullable
    def objectifs(self, value):
        if value is None:
            self._objectifs = None
            return
        self._objectifs = value

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
    def version(self):
        return self._version

    @version.setter
    @typed(str)
    def version(self, value):
        if value is None:
            raise ValidationError("version", 'La propriété "version" ne peut pas être nulle.')
        self._version = value

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
    def auteur_id(self):
        return self._auteur_id

    @auteur_id.setter
    @typed(int)
    def auteur_id(self, value):
        if value is None:
            raise ValidationError("auteur_id", 'La propriété "auteur_id" ne peut pas être nulle.')
        self._auteur_id = value

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
            "titre": self.titre,
            "intention": self.intention,
            "objectifs": self.objectifs,
            "statut": self.statut,
            "version": self.version,
            "referentiel_id": self.referentiel_id,
            "auteur_id": self.auteur_id,
            "created_at": None if self.created_at is None else self.created_at.isoformat(),
            "updated_at": None if self.updated_at is None else self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ScenarioBase":
        return cls(
            id=data["id"],
            titre=data["titre"],
            intention=data["intention"],
            objectifs=data["objectifs"],
            statut=data["statut"],
            version=data["version"],
            referentiel_id=data["referentiel_id"],
            auteur_id=data["auteur_id"],
            created_at=cls._coerce_datetime(data.get("created_at")),
            updated_at=cls._coerce_datetime(data.get("updated_at")),
        )

    def __repr__(self) -> str:
        return f"ScenarioBase(id={self.id!r}, titre={self.titre!r}, intention={self.intention!r}, objectifs={self.objectifs!r}, statut={self.statut!r}, version={self.version!r}, referentiel_id={self.referentiel_id!r}, auteur_id={self.auteur_id!r}, created_at={self.created_at!r}, updated_at={self.updated_at!r})"

