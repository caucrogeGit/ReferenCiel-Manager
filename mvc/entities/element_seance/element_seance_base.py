"""FICHIER GENERE PAR FORGE.
Base regenerable de l'entite ElementSeance.
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


class ElementSeanceBase:
    """Classe de base regenerable de ElementSeance."""

    def __init__(self, ordre, type, titre, obligatoire, seance_id, created_at, updated_at, id=None, contenu=None, duree_minutes=None, role_pedagogique=None, qcm_id=None, checklist_id=None):
        self.ordre = ordre
        self.type = type
        self.titre = titre
        self.obligatoire = obligatoire
        self.seance_id = seance_id
        self.created_at = created_at
        self.updated_at = updated_at
        self.id = id
        self.contenu = contenu
        self.duree_minutes = duree_minutes
        self.role_pedagogique = role_pedagogique
        self.qcm_id = qcm_id
        self.checklist_id = checklist_id

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
    def duree_minutes(self):
        return self._duree_minutes

    @duree_minutes.setter
    @typed(int)
    @nullable
    def duree_minutes(self, value):
        if value is None:
            self._duree_minutes = None
            return
        self._duree_minutes = value

    @property
    def obligatoire(self):
        return self._obligatoire

    @obligatoire.setter
    @typed(bool)
    def obligatoire(self, value):
        if value is None:
            raise ValidationError("obligatoire", 'La propriété "obligatoire" ne peut pas être nulle.')
        self._obligatoire = value

    @property
    def role_pedagogique(self):
        return self._role_pedagogique

    @role_pedagogique.setter
    @typed(str)
    @nullable
    def role_pedagogique(self, value):
        if value is None:
            self._role_pedagogique = None
            return
        self._role_pedagogique = value

    @property
    def seance_id(self):
        return self._seance_id

    @seance_id.setter
    @typed(int)
    def seance_id(self, value):
        if value is None:
            raise ValidationError("seance_id", 'La propriété "seance_id" ne peut pas être nulle.')
        self._seance_id = value

    @property
    def qcm_id(self):
        return self._qcm_id

    @qcm_id.setter
    @typed(int)
    @nullable
    def qcm_id(self, value):
        if value is None:
            self._qcm_id = None
            return
        self._qcm_id = value

    @property
    def checklist_id(self):
        return self._checklist_id

    @checklist_id.setter
    @typed(int)
    @nullable
    def checklist_id(self, value):
        if value is None:
            self._checklist_id = None
            return
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
            "ordre": self.ordre,
            "type": self.type,
            "titre": self.titre,
            "contenu": self.contenu,
            "duree_minutes": self.duree_minutes,
            "obligatoire": self.obligatoire,
            "role_pedagogique": self.role_pedagogique,
            "seance_id": self.seance_id,
            "qcm_id": self.qcm_id,
            "checklist_id": self.checklist_id,
            "created_at": None if self.created_at is None else self.created_at.isoformat(),
            "updated_at": None if self.updated_at is None else self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ElementSeanceBase":
        return cls(
            id=data["id"],
            ordre=data["ordre"],
            type=data["type"],
            titre=data["titre"],
            contenu=data["contenu"],
            duree_minutes=data["duree_minutes"],
            obligatoire=data["obligatoire"],
            role_pedagogique=data["role_pedagogique"],
            seance_id=data["seance_id"],
            qcm_id=data["qcm_id"],
            checklist_id=data["checklist_id"],
            created_at=cls._coerce_datetime(data.get("created_at")),
            updated_at=cls._coerce_datetime(data.get("updated_at")),
        )

    def __repr__(self) -> str:
        return f"ElementSeanceBase(id={self.id!r}, ordre={self.ordre!r}, type={self.type!r}, titre={self.titre!r}, contenu={self.contenu!r}, duree_minutes={self.duree_minutes!r}, obligatoire={self.obligatoire!r}, role_pedagogique={self.role_pedagogique!r}, seance_id={self.seance_id!r}, qcm_id={self.qcm_id!r}, checklist_id={self.checklist_id!r}, created_at={self.created_at!r}, updated_at={self.updated_at!r})"

