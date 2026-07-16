# pyright: strict
"""Espace élève v2 — déposer un fichier pour l'activité d'une séance.

Route gardée par `espace_eleve.voir` (préfixe `/ma-sequence`) + contrôle
d'appartenance dans le modèle. L'upload délègue à l'opt-in `files`
(`save_upload` : allowlist d'extensions/MIME + taille max) ; on ne stocke que le
chemin retourné dans `depot_eleve.Fichier`.
"""
from __future__ import annotations

from core.auth.session import get_authenticated_user_id
from core.http.request import Request
from core.http.response import Response
from core.mvc.controller import BaseController
from core.security.session import get_flash, get_session_id
from forge_mvc_files import UploadError, save_upload

from mvc.models.depot_saisie_model import enregistrer_depot, get_activite_depots


class DepotEleveSaisieController:
    @staticmethod
    def show(request: Request) -> Response:
        """L'activité et les dépôts (`GET /ma-sequence/depot/<progression_seance_id>`)."""
        user_id = get_authenticated_user_id(request)
        pp_id = int(request.route("id") or "0")
        data = get_activite_depots(pp_id, user_id) if user_id is not None else None
        if data is None:
            return BaseController.not_found()
        return BaseController.render(
            "app/ma_sequence/depot.html",
            context={"activite": data, "flash": get_flash(get_session_id(request))},
            request=request,
        )

    @staticmethod
    def submit(request: Request) -> Response:
        """Reçoit et enregistre un dépôt (`POST /ma-sequence/depot/<progression_seance_id>`)."""
        user_id = get_authenticated_user_id(request)
        pp_id = int(request.route("id") or "0")
        data = get_activite_depots(pp_id, user_id) if user_id is not None else None
        if data is None or user_id is None:
            return BaseController.not_found()

        cible = f"/ma-sequence/depot/{pp_id}"
        uploaded = request.file("fichier")
        if uploaded is None or not uploaded.filename:
            return BaseController.redirect_with_flash(request, cible, "Aucun fichier sélectionné.", "error")

        try:
            saved = save_upload(uploaded, category="depots")
        except UploadError as exc:
            return BaseController.redirect_with_flash(request, cible, f"Dépôt refusé : {exc}", "error")

        resultat = enregistrer_depot(pp_id, user_id, saved.path)
        if resultat is None:
            return BaseController.not_found()
        return BaseController.redirect_with_flash(request, cible, "Fichier déposé.", "success")
