"""FICHIER GENERE PAR FORGE.
Base regenerable de l'entite Sequence.
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


class SequenceBase:
    """Classe de base regenerable de Sequence."""

    def __init__(self, identifiant, titre, statut, activite_glissante, ordre_impose, created_at, updated_at, id=None, presentation=None, prerequis=None, positionnement_progression=None, duree_estimee=None, modalites_evaluation=None, niveau_classe_id=None):
        self.identifiant = identifiant
        self.titre = titre
        self.statut = statut
        self.activite_glissante = activite_glissante
        self.ordre_impose = ordre_impose
        self.created_at = created_at
        self.updated_at = updated_at
        self.id = id
        self.presentation = presentation
        self.prerequis = prerequis
        self.positionnement_progression = positionnement_progression
        self.duree_estimee = duree_estimee
        self.modalites_evaluation = modalites_evaluation
        self.niveau_classe_id = niveau_classe_id

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
    def identifiant(self):
        return self._identifiant

    @identifiant.setter
    @typed(str)
    def identifiant(self, value):
        if value is None:
            raise ValidationError("identifiant", 'La propriété "identifiant" ne peut pas être nulle.')
        self._identifiant = value

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
    def presentation(self):
        return self._presentation

    @presentation.setter
    @typed(str)
    @nullable
    def presentation(self, value):
        if value is None:
            self._presentation = None
            return
        self._presentation = value

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
    def activite_glissante(self):
        return self._activite_glissante

    @activite_glissante.setter
    @typed(bool)
    def activite_glissante(self, value):
        if value is None:
            raise ValidationError("activite_glissante", 'La propriété "activite_glissante" ne peut pas être nulle.')
        self._activite_glissante = value

    @property
    def ordre_impose(self):
        return self._ordre_impose

    @ordre_impose.setter
    @typed(bool)
    def ordre_impose(self, value):
        if value is None:
            raise ValidationError("ordre_impose", 'La propriété "ordre_impose" ne peut pas être nulle.')
        self._ordre_impose = value

    @property
    def prerequis(self):
        return self._prerequis

    @prerequis.setter
    @typed(str)
    @nullable
    def prerequis(self, value):
        if value is None:
            self._prerequis = None
            return
        self._prerequis = value

    @property
    def positionnement_progression(self):
        return self._positionnement_progression

    @positionnement_progression.setter
    @typed(str)
    @nullable
    def positionnement_progression(self, value):
        if value is None:
            self._positionnement_progression = None
            return
        self._positionnement_progression = value

    @property
    def duree_estimee(self):
        return self._duree_estimee

    @duree_estimee.setter
    @typed(str)
    @nullable
    def duree_estimee(self, value):
        if value is None:
            self._duree_estimee = None
            return
        self._duree_estimee = value

    @property
    def modalites_evaluation(self):
        return self._modalites_evaluation

    @modalites_evaluation.setter
    @typed(str)
    @nullable
    def modalites_evaluation(self, value):
        if value is None:
            self._modalites_evaluation = None
            return
        self._modalites_evaluation = value

    @property
    def niveau_classe_id(self):
        return self._niveau_classe_id

    @niveau_classe_id.setter
    @typed(int)
    @nullable
    def niveau_classe_id(self, value):
        if value is None:
            self._niveau_classe_id = None
            return
        self._niveau_classe_id = value

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
            "identifiant": self.identifiant,
            "titre": self.titre,
            "presentation": self.presentation,
            "statut": self.statut,
            "activite_glissante": self.activite_glissante,
            "ordre_impose": self.ordre_impose,
            "prerequis": self.prerequis,
            "positionnement_progression": self.positionnement_progression,
            "duree_estimee": self.duree_estimee,
            "modalites_evaluation": self.modalites_evaluation,
            "niveau_classe_id": self.niveau_classe_id,
            "created_at": None if self.created_at is None else self.created_at.isoformat(),
            "updated_at": None if self.updated_at is None else self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SequenceBase":
        return cls(
            id=data["id"],
            identifiant=data["identifiant"],
            titre=data["titre"],
            presentation=data["presentation"],
            statut=data["statut"],
            activite_glissante=data["activite_glissante"],
            ordre_impose=data["ordre_impose"],
            prerequis=data["prerequis"],
            positionnement_progression=data["positionnement_progression"],
            duree_estimee=data["duree_estimee"],
            modalites_evaluation=data["modalites_evaluation"],
            niveau_classe_id=data["niveau_classe_id"],
            created_at=cls._coerce_datetime(data.get("created_at")),
            updated_at=cls._coerce_datetime(data.get("updated_at")),
        )

    def __repr__(self) -> str:
        return f"SequenceBase(id={self.id!r}, identifiant={self.identifiant!r}, titre={self.titre!r}, presentation={self.presentation!r}, statut={self.statut!r}, activite_glissante={self.activite_glissante!r}, ordre_impose={self.ordre_impose!r}, prerequis={self.prerequis!r}, positionnement_progression={self.positionnement_progression!r}, duree_estimee={self.duree_estimee!r}, modalites_evaluation={self.modalites_evaluation!r}, niveau_classe_id={self.niveau_classe_id!r}, created_at={self.created_at!r}, updated_at={self.updated_at!r})"

