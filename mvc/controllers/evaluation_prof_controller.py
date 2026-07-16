# pyright: strict
"""Évaluation professeur — détail d'une progression, validation, confirmation checklist.

Routes gardées par `execution.gerer` (préfixe `/evaluation`) : réservées au
professeur (et à l'admin). Écritures POST protégées par CSRF (défaut Forge).
"""
from __future__ import annotations

from core.auth.session import get_authenticated_user_id
from core.http.request import Request
from core.http.response import Response
from core.mvc.controller import BaseController
from core.security.session import get_flash, get_session_id

from mvc.models.evaluation_prof_model import (
    STATUTS_SEANCE,
    enregistrer_coches_prof,
    get_checklist_review,
    get_progression_detail,
    set_seance_statut,
)
from mvc.models.notation_critere_model import enregistrer_notation, get_grille


class EvaluationProfController:
    @staticmethod
    def progression(request: Request) -> Response:
        """Détail d'une progression élève (`GET /evaluation/progression/<progression_id>`)."""
        progression_id = int(request.route("id") or "0")
        data = get_progression_detail(progression_id)
        if data is None:
            return BaseController.not_found()
        return BaseController.render(
            "app/evaluation/progression.html",
            context={
                "progression": data,
                "statuts": STATUTS_SEANCE,
                "flash": get_flash(get_session_id(request)),
            },
            request=request,
        )

    @staticmethod
    def set_statut(request: Request) -> Response:
        """Pose le statut d'une séance (`POST /evaluation/seance/<progression_seance_id>/statut`)."""
        pp_id = int(request.route("id") or "0")
        statut = request.form("statut", "")
        progression_id = request.form("progression_id", "0")
        cible = f"/evaluation/progression/{progression_id}"
        if set_seance_statut(pp_id, statut):
            return BaseController.redirect_with_flash(request, cible, f"Séance mise à jour : {statut}.", "success")
        return BaseController.redirect_with_flash(request, cible, "Statut invalide.", "error")

    @staticmethod
    def checklist(request: Request) -> Response:
        """Revue de la checklist d'une séance (`GET /evaluation/checklist/<progression_seance_id>`)."""
        pp_id = int(request.route("id") or "0")
        data = get_checklist_review(pp_id)
        if data is None:
            return BaseController.not_found()
        return BaseController.render(
            "app/evaluation/checklist.html",
            context={"checklist": data, "flash": get_flash(get_session_id(request))},
            request=request,
        )

    @staticmethod
    def coche(request: Request) -> Response:
        """Confirme la checklist (`POST /evaluation/checklist/<progression_seance_id>`)."""
        pp_id = int(request.route("id") or "0")
        data = get_checklist_review(pp_id)
        if data is None:
            return BaseController.not_found()
        coches: set[int] = set()
        for section in data["sections"]:
            for item in section["items"]:
                iid = int(item["id"])
                if request.form(f"item_{iid}", ""):
                    coches.add(iid)
        resultat = enregistrer_coches_prof(pp_id, coches)
        if resultat is None:
            return BaseController.not_found()
        cible = f"/evaluation/progression/{data['progression_id']}"
        message = f"Checklist confirmée : {resultat['coches']} / {resultat['items']} items validés."
        return BaseController.redirect_with_flash(request, cible, message, "success")

    @staticmethod
    def activite(request: Request) -> Response:
        """Grille de notation par critères (`GET /evaluation/activite/<progression_seance_id>`)."""
        pp_id = int(request.route("id") or "0")
        data = get_grille(pp_id)
        if data is None:
            return BaseController.not_found()
        return BaseController.render(
            "app/evaluation/activite.html",
            context={"grille": data, "flash": get_flash(get_session_id(request))},
            request=request,
        )

    @staticmethod
    def noter(request: Request) -> Response:
        """Enregistre la notation (`POST /evaluation/activite/<progression_seance_id>`)."""
        pp_id = int(request.route("id") or "0")
        data = get_grille(pp_id)
        if data is None:
            return BaseController.not_found()
        niveaux: dict[int, str] = {}
        for competence in data["competences"]:
            for critere in competence["criteres"]:
                cid = int(critere["id"])
                niveau = request.form(f"critere_{cid}", "")
                if niveau:
                    niveaux[cid] = niveau
        resultat = enregistrer_notation(pp_id, niveaux, get_authenticated_user_id(request))
        if resultat is None:
            return BaseController.not_found()
        cible = f"/evaluation/progression/{data['progression_id']}"
        message = f"Notation enregistrée : {resultat['notes']} critère(s) noté(s)."
        return BaseController.redirect_with_flash(request, cible, message, "success")
