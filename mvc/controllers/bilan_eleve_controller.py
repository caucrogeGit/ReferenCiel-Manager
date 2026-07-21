# pyright: strict
"""Bilan de maîtrise (ADR-032/033) : le professeur **arrête** une synthèse d'évaluation.

Le professeur **connecté** liste les bilans, prépare un nouveau bilan (choix d'une
progression de sa classe → écran d'**arbitrage** : la maîtrise de chaque compétence
est **suggérée** par l'agrégat des critères de la feuille, le professeur la retient
ou l'ajuste → appréciation globale + statut), puis fige la synthèse. Route protégée
par `execution.gerer` (rôles `admin` et `professeur`) ; l'auteur est déduit du compte
(`professeur.UserId`). Un compte non rattaché voit un message explicite.
"""
from __future__ import annotations

from typing import Any

from core.auth.session import get_authenticated_user_id
from core.http.request import Request
from core.http.response import Response
from core.mvc.controller import BaseController

from mvc.models.bilan_eleve_model import (
    NIVEAUX_BILAN,
    apercu_synthese,
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
        """Choix d'une progression à évaluer (`GET /bilan/new`)."""
        professeur = _professeur_connecte(request)
        progressions = progressions_evaluables(int(professeur["id"])) if professeur is not None else []
        return BaseController.render(
            "app/bilan_eleve/form.html",
            context={"professeur": professeur, "progressions": progressions},
            request=request,
        )

    @staticmethod
    def preparer(request: Request) -> Response:
        """Écran d'arbitrage : suggestions par compétence à retenir/ajuster
        (`GET /bilan/preparer?progression_id=<id>`)."""
        professeur = _professeur_connecte(request)
        if professeur is None:
            return BaseController.render(
                "app/bilan_eleve/form.html",
                context={"professeur": None, "progressions": []},
                request=request,
            )
        progression_raw = request.query("progression_id", "")
        apercu = apercu_synthese(int(progression_raw)) if progression_raw.isdigit() else None
        if apercu is None:
            return BaseController.redirect_with_flash(
                request, "/bilan/new", "Sélectionnez une progression d'élève.", "error"
            )
        return BaseController.render(
            "app/bilan_eleve/preparer.html",
            context={
                "apercu": apercu,
                "statuts": _STATUTS,
                "niveaux_bilan": NIVEAUX_BILAN,
                "erreurs": [],
                "valeurs": {"appreciation": "", "statut": "brouillon"},
            },
            request=request,
        )

    @staticmethod
    def create(request: Request) -> Response:
        """Fige la synthèse arrêtée (`POST /bilan/create`)."""
        professeur = _professeur_connecte(request)
        progression_raw = request.form("progression_id", "")
        appreciation = request.form("appreciation", "").strip()
        statut = request.form("statut", "brouillon")

        apercu = apercu_synthese(int(progression_raw)) if progression_raw.isdigit() else None
        erreurs: list[str] = []
        if professeur is None:
            erreurs.append("Votre compte n'est rattaché à aucune fiche professeur.")
        if not appreciation:
            erreurs.append("L'appréciation globale est obligatoire.")
        if statut not in _STATUTS:
            erreurs.append("Statut invalide.")

        if apercu is None or professeur is None:
            return BaseController.redirect_with_flash(
                request, "/bilan/new", "Sélectionnez une progression d'élève.", "error"
            )
        if erreurs:
            return BaseController.render(
                "app/bilan_eleve/preparer.html",
                status=422,
                context={
                    "apercu": apercu,
                    "statuts": _STATUTS,
                    "niveaux_bilan": NIVEAUX_BILAN,
                    "erreurs": erreurs,
                    "valeurs": {"appreciation": appreciation, "statut": statut},
                },
                request=request,
            )

        niveaux_arretes: dict[int, str] = {}
        for comp in apercu["synthese"]:
            cid = int(comp["competence_id"])
            val = request.form(f"niveau_{cid}", "")
            if val:
                niveaux_arretes[cid] = val

        bilan_id = creer_bilan(
            progression_sequence_id=int(progression_raw),
            professeur_id=int(professeur["id"]),
            appreciation=appreciation,
            statut=statut,
            niveaux_arretes=niveaux_arretes,
        )
        if bilan_id is None:
            return BaseController.redirect_with_flash(
                request, "/bilan/new", "Progression introuvable.", "error"
            )
        return BaseController.redirect_with_flash(
            request, f"/bilan/show/{bilan_id}", "Bilan de maîtrise arrêté.", "success"
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
