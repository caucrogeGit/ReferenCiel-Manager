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

    def __init__(self, titre, intention, statut, version, created_at, updated_at, id=None, objectifs=None, description_contexte=None, problematique=None, materiels_logiciels=None, liens_associes=None, espaces_formation=None, co_intervention=False, referentiel_id=None, auteur_id=None):
        self.titre = titre
        self.intention = intention
        self.statut = statut
        self.version = version
        self.created_at = created_at
        self.updated_at = updated_at
        self.id = id
        self.objectifs = objectifs
        self.description_contexte = description_contexte
        self.problematique = problematique
        self.materiels_logiciels = materiels_logiciels
        self.liens_associes = liens_associes
        self.espaces_formation = espaces_formation
        self.co_intervention = co_intervention
        self.referentiel_id = referentiel_id
        self.auteur_id = auteur_id

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
    def description_contexte(self):
        return self._description_contexte

    @description_contexte.setter
    @typed(str)
    @nullable
    def description_contexte(self, value):
        if value is None:
            self._description_contexte = None
            return
        self._description_contexte = value

    @property
    def problematique(self):
        return self._problematique

    @problematique.setter
    @typed(str)
    @nullable
    def problematique(self, value):
        if value is None:
            self._problematique = None
            return
        self._problematique = value

    @property
    def materiels_logiciels(self):
        return self._materiels_logiciels

    @materiels_logiciels.setter
    @typed(str)
    @nullable
    def materiels_logiciels(self, value):
        if value is None:
            self._materiels_logiciels = None
            return
        self._materiels_logiciels = value

    @property
    def liens_associes(self):
        return self._liens_associes

    @liens_associes.setter
    @typed(str)
    @nullable
    def liens_associes(self, value):
        if value is None:
            self._liens_associes = None
            return
        self._liens_associes = value

    @property
    def espaces_formation(self):
        return self._espaces_formation

    @espaces_formation.setter
    @typed(str)
    @nullable
    def espaces_formation(self, value):
        if value is None:
            self._espaces_formation = None
            return
        self._espaces_formation = value

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
    def co_intervention(self):
        return self._co_intervention

    @co_intervention.setter
    @typed(bool)
    def co_intervention(self, value):
        if value is None:
            raise ValidationError("co_intervention", 'La propriété "co_intervention" ne peut pas être nulle.')
        self._co_intervention = value

    @property
    def referentiel_id(self):
        return self._referentiel_id

    @referentiel_id.setter
    @typed(int)
    @nullable
    def referentiel_id(self, value):
        if value is None:
            self._referentiel_id = None
            return
        self._referentiel_id = value

    @property
    def auteur_id(self):
        return self._auteur_id

    @auteur_id.setter
    @typed(int)
    @nullable
    def auteur_id(self, value):
        if value is None:
            self._auteur_id = None
            return
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
            "description_contexte": self.description_contexte,
            "problematique": self.problematique,
            "materiels_logiciels": self.materiels_logiciels,
            "liens_associes": self.liens_associes,
            "espaces_formation": self.espaces_formation,
            "statut": self.statut,
            "version": self.version,
            "co_intervention": self.co_intervention,
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
            description_contexte=data["description_contexte"],
            problematique=data["problematique"],
            materiels_logiciels=data["materiels_logiciels"],
            liens_associes=data["liens_associes"],
            espaces_formation=data["espaces_formation"],
            statut=data["statut"],
            version=data["version"],
            co_intervention=data["co_intervention"],
            referentiel_id=data["referentiel_id"],
            auteur_id=data["auteur_id"],
            created_at=cls._coerce_datetime(data.get("created_at")),
            updated_at=cls._coerce_datetime(data.get("updated_at")),
        )

    def __repr__(self) -> str:
        return f"ScenarioBase(id={self.id!r}, titre={self.titre!r}, intention={self.intention!r}, objectifs={self.objectifs!r}, description_contexte={self.description_contexte!r}, problematique={self.problematique!r}, materiels_logiciels={self.materiels_logiciels!r}, liens_associes={self.liens_associes!r}, espaces_formation={self.espaces_formation!r}, statut={self.statut!r}, version={self.version!r}, co_intervention={self.co_intervention!r}, referentiel_id={self.referentiel_id!r}, auteur_id={self.auteur_id!r}, created_at={self.created_at!r}, updated_at={self.updated_at!r})"

