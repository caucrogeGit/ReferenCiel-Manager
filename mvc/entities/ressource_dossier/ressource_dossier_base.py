"""FICHIER GENERE PAR FORGE.
Base regenerable de l'entite RessourceDossier.
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


class RessourceDossierBase:
    """Classe de base regenerable de RessourceDossier."""

    def __init__(self, type, titre, ordre, dossier_technique_id, created_at, updated_at, id=None, contenu=None, media_ref=None, url=None):
        self.type = type
        self.titre = titre
        self.ordre = ordre
        self.dossier_technique_id = dossier_technique_id
        self.created_at = created_at
        self.updated_at = updated_at
        self.id = id
        self.contenu = contenu
        self.media_ref = media_ref
        self.url = url

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
    def type(self):
        return self._type

    @type.setter
    @typed(str)
    def type(self, value):
        if value is None:
            raise ValidationError("type", 'La propriété "type" ne peut pas être nulle.')
        self._type = value

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
    def ordre(self):
        return self._ordre

    @ordre.setter
    @typed(int)
    def ordre(self, value):
        if value is None:
            raise ValidationError("ordre", 'La propriété "ordre" ne peut pas être nulle.')
        self._ordre = value

    @property
    def contenu(self):
        return self._contenu

    @contenu.setter
    @typed(str)
    @nullable
    def contenu(self, value):
        if value is None:
            self._contenu = None
            return
        self._contenu = value

    @property
    def media_ref(self):
        return self._media_ref

    @media_ref.setter
    @typed(str)
    @nullable
    def media_ref(self, value):
        if value is None:
            self._media_ref = None
            return
        self._media_ref = value

    @property
    def url(self):
        return self._url

    @url.setter
    @typed(str)
    @nullable
    def url(self, value):
        if value is None:
            self._url = None
            return
        self._url = value

    @property
    def dossier_technique_id(self):
        return self._dossier_technique_id

    @dossier_technique_id.setter
    @typed(int)
    def dossier_technique_id(self, value):
        if value is None:
            raise ValidationError("dossier_technique_id", 'La propriété "dossier_technique_id" ne peut pas être nulle.')
        self._dossier_technique_id = value

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
            "type": self.type,
            "titre": self.titre,
            "ordre": self.ordre,
            "contenu": self.contenu,
            "media_ref": self.media_ref,
            "url": self.url,
            "dossier_technique_id": self.dossier_technique_id,
            "created_at": None if self.created_at is None else self.created_at.isoformat(),
            "updated_at": None if self.updated_at is None else self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RessourceDossierBase":
        return cls(
            id=data["id"],
            type=data["type"],
            titre=data["titre"],
            ordre=data["ordre"],
            contenu=data["contenu"],
            media_ref=data["media_ref"],
            url=data["url"],
            dossier_technique_id=data["dossier_technique_id"],
            created_at=cls._coerce_datetime(data.get("created_at")),
            updated_at=cls._coerce_datetime(data.get("updated_at")),
        )

    def __repr__(self) -> str:
        return f"RessourceDossierBase(id={self.id!r}, type={self.type!r}, titre={self.titre!r}, ordre={self.ordre!r}, contenu={self.contenu!r}, media_ref={self.media_ref!r}, url={self.url!r}, dossier_technique_id={self.dossier_technique_id!r}, created_at={self.created_at!r}, updated_at={self.updated_at!r})"

