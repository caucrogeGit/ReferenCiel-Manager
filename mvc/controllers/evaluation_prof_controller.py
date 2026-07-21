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

from mvc.helpers.htmx import est_htmx
from mvc.services.niveaux_maitrise import NIVEAUX
from mvc.models.evaluation_prof_model import (
    STATUTS_SEANCE,
    enregistrer_coches_prof,
    get_checklist_review,
    get_progression_detail,
    set_seance_statut,
)
from mvc.models.notation_critere_model import (
    contexte_critere,
    enregistrer_notes,
    get_grille,
    indicateurs_du_critere,
    maj_indicateurs_observes,
    positionner_niveau,
    professeur_de_user,
)


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
    def _professeur_id(request: Request) -> "int | None":
        user_id = get_authenticated_user_id(request)
        return professeur_de_user(user_id) if user_id is not None else None

    @staticmethod
    def activite(request: Request) -> Response:
        """Feuille de positionnement (`GET /evaluation/activite/<progression_seance_id>`)."""
        pp_id = int(request.route("id") or "0")
        data = get_grille(pp_id)
        if data is None:
            return BaseController.not_found()
        return BaseController.render(
            "app/evaluation/activite.html",
            context={
                "grille": data,
                "niveaux": NIVEAUX,
                "base": f"/evaluation/activite/{pp_id}",
                "peut_editer": EvaluationProfController._professeur_id(request) is not None,
                "flash": get_flash(get_session_id(request)),
            },
            request=request,
        )

    @staticmethod
    def _rendre_critere(request: Request, pp_id: int, critere_id: int) -> Response:
        """Re-rend le fragment d'un critère (HTMX) ou renvoie à la feuille (sans JS)."""
        if not est_htmx(request):
            return BaseController.redirect(f"/evaluation/activite/{pp_id}", request=request)
        critere = contexte_critere(pp_id, critere_id)
        if critere is None:
            return BaseController.not_found()
        return BaseController.render(
            "app/evaluation/_critere.html",
            context={"c": critere, "niveaux": NIVEAUX, "base": f"/evaluation/activite/{pp_id}"},
            request=request,
        )

    @staticmethod
    def positionner(request: Request) -> Response:
        """Positionne un critère à un niveau (`POST /evaluation/activite/<id>/critere/<cid>/niveau`)."""
        pp_id = int(request.route("id") or "0")
        cid = int(request.route("cid") or "0")
        prof_id = EvaluationProfController._professeur_id(request)
        if prof_id is not None:
            positionner_niveau(pp_id, prof_id, cid, request.form("niveau", ""))
        return EvaluationProfController._rendre_critere(request, pp_id, cid)

    @staticmethod
    def cocher_indicateurs(request: Request) -> Response:
        """Met à jour les indicateurs cochés d'un critère
        (`POST /evaluation/activite/<id>/critere/<cid>/indicateurs`)."""
        pp_id = int(request.route("id") or "0")
        cid = int(request.route("cid") or "0")
        prof_id = EvaluationProfController._professeur_id(request)
        if prof_id is not None:
            coches = {
                int(ind["id"])
                for ind in indicateurs_du_critere(cid)
                if request.form(f"indicateur_{ind['id']}", "")
            }
            maj_indicateurs_observes(pp_id, prof_id, cid, coches)
        return EvaluationProfController._rendre_critere(request, pp_id, cid)

    @staticmethod
    def notes(request: Request) -> Response:
        """Enregistre production/aide/appréciation (`POST /evaluation/activite/<id>/notes`)."""
        pp_id = int(request.route("id") or "0")
        prof_id = EvaluationProfController._professeur_id(request)
        if prof_id is not None:
            enregistrer_notes(
                pp_id,
                prof_id,
                (request.form("production", "") or "").strip() or None,
                (request.form("aide", "") or "").strip() or None,
                (request.form("appreciation", "") or "").strip() or None,
            )
        if est_htmx(request):
            return BaseController.render(
                "app/evaluation/_sauvegarde_oob.html", context={}, request=request
            )
        return BaseController.redirect(f"/evaluation/activite/{pp_id}", request=request)
