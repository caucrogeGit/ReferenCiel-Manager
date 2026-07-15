# pyright: strict
"""Bilan élève (ticket 21) : le professeur **arrête** une synthèse d'évaluation.

Le professeur **connecté** liste les bilans, en crée un nouveau (choix d'une
progression → la synthèse par compétence est **figée** à la création → appréciation
globale + statut), et consulte un bilan existant. Route protégée par `execution.gerer`
(rôles `admin` et `professeur`) ; l'auteur est déduit du compte (`professeur.UserId`).
Un compte non rattaché à un professeur voit un message explicite.
"""
from __future__ import annotations

from typing import Any

from core.auth.session import get_authenticated_user_id
from core.http.request import Request
from core.http.response import Response
from core.mvc.controller import BaseController

from mvc.models.bilan_eleve_model import (
    creer_bilan,
    get_bilan,
    list_bilans,
    progressions_evaluables,
)
from mvc.models.mes_classes_model import get_professeur_by_user

_STATUTS = ("brouillon", "publie", "archive")


def _professeur_connecte(request: Request) -> dict[str, Any] | None:
    user_id = get_authenticated_user_id(request)
    return get_professeur_by_user(user_id) if user_id is not None else None


class BilanEleveController:
    @staticmethod
    def index(request: Request) -> Response:
        """Liste des bilans (`GET /bilan`)."""
        return BaseController.render(
            "app/bilan_eleve/index.html",
            context={"bilans": list_bilans()},
            request=request,
        )

    @staticmethod
    def new(request: Request) -> Response:
        """Formulaire de création (`GET /bilan/new`)."""
        professeur = _professeur_connecte(request)
        return BaseController.render(
            "app/bilan_eleve/form.html",
            context={
                "professeur": professeur,
                "progressions": progressions_evaluables(),
                "statuts": _STATUTS,
                "erreurs": [],
                "valeurs": {"progression_id": "", "appreciation": "", "statut": "brouillon"},
            },
            request=request,
        )

    @staticmethod
    def create(request: Request) -> Response:
        """Crée le bilan en figeant la synthèse (`POST /bilan/create`)."""
        professeur = _professeur_connecte(request)
        progression_raw = request.form("progression_id", "")
        appreciation = request.form("appreciation", "").strip()
        statut = request.form("statut", "brouillon")

        erreurs: list[str] = []
        if professeur is None:
            erreurs.append("Votre compte n'est rattaché à aucune fiche professeur.")
        if not progression_raw.isdigit():
            erreurs.append("Sélectionnez une progression d'élève.")
        if not appreciation:
            erreurs.append("L'appréciation globale est obligatoire.")
        if statut not in _STATUTS:
            erreurs.append("Statut invalide.")

        if erreurs or professeur is None:
            return BaseController.render(
                "app/bilan_eleve/form.html",
                status=422,
                context={
                    "professeur": professeur,
                    "progressions": progressions_evaluables(),
                    "statuts": _STATUTS,
                    "erreurs": erreurs,
                    "valeurs": {
                        "progression_id": progression_raw,
                        "appreciation": appreciation,
                        "statut": statut,
                    },
                },
                request=request,
            )

        bilan_id = creer_bilan(
            progression_parcours_id=int(progression_raw),
            professeur_id=int(professeur["id"]),
            appreciation=appreciation,
            statut=statut,
        )
        if bilan_id is None:
            return BaseController.render(
                "app/bilan_eleve/form.html",
                status=422,
                context={
                    "professeur": professeur,
                    "progressions": progressions_evaluables(),
                    "statuts": _STATUTS,
                    "erreurs": ["Progression introuvable."],
                    "valeurs": {
                        "progression_id": progression_raw,
                        "appreciation": appreciation,
                        "statut": statut,
                    },
                },
                request=request,
            )
        return BaseController.redirect_with_flash(
            request, f"/bilan/show/{bilan_id}", "Bilan créé et synthèse figée.", "success"
        )

    @staticmethod
    def show(request: Request) -> Response:
        """Consultation d'un bilan (`GET /bilan/show/<id>`)."""
        bilan_id = int(request.route("id") or "0")
        bilan = get_bilan(bilan_id)
        if bilan is None:
            return BaseController.not_found()
        return BaseController.render(
            "app/bilan_eleve/show.html",
            context={"bilan": bilan},
            request=request,
        )
