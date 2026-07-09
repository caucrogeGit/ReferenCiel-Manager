# pyright: strict
"""Import d'un référentiel niveau-classe par upload admin (ticket 11, ADR-008).

Flux POST : fichier reçu → JSON lisible ? → **validation** contre le schéma (ticket 04)
→ **type d'enveloppe** attendu ? → fichier **conservé** (provenance, forge-mvc-files)
→ **import** (`import_referentiel`) → **rapport** best-effort (ADR-010).

Route non publique (session requise). RBAC (rôle `admin`) différé : à border quand
l'opt-in `rbac` sera installé.
"""
from __future__ import annotations

import json
from typing import Any, cast

from core.http.request import Request
from core.http.response import Response
from core.mvc.controller import BaseController
from forge_mvc_files import UploadError, save_upload

from mvc.services.canonical_validator import validate_referentiel_canonical
from mvc.services.referentiel_importer import import_referentiel

_TYPE_ATTENDU = "referentiel_niveau_classe"


def _refuser(request: Request, messages: list[str], titre: str = "Import refusé") -> Response:
    """Ré-affiche le formulaire avec les messages d'erreur (rien n'est importé)."""
    return BaseController.render(
        "referentiel_import/form.html",
        status=400,
        context={"erreurs": messages, "titre_erreur": titre},
        request=request,
    )


class ReferentielImportController:
    @staticmethod
    def form(request: Request) -> Response:
        """Formulaire d'upload (`GET /admin/referentiel/import`)."""
        return BaseController.render(
            "referentiel_import/form.html", context={}, request=request
        )

    @staticmethod
    def upload(request: Request) -> Response:
        """Traite l'upload (`POST /admin/referentiel/import`)."""
        uploaded = request.file("fichier")
        if uploaded is None or not uploaded.filename:
            return _refuser(request, ["Aucun fichier reçu."])

        try:
            canonical: Any = json.loads(uploaded.content)
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            return _refuser(request, [f"JSON illisible : {exc}"])

        erreurs = validate_referentiel_canonical(canonical)
        if erreurs:
            return _refuser(request, erreurs, titre="Fichier non conforme au schéma")

        # Le document est conforme au schéma → c'est un objet ; on le type explicitement.
        canonique = cast("dict[str, Any]", canonical)
        type_env = canonique.get("type")
        if type_env != _TYPE_ATTENDU:
            return _refuser(
                request,
                [f"Type d'enveloppe inattendu : {type_env!r} (attendu : {_TYPE_ATTENDU!r})."],
            )

        try:
            saved = save_upload(uploaded, category="referentiels")
        except UploadError as exc:
            return _refuser(request, [f"Échec de l'enregistrement du fichier : {exc}"])

        rapport = import_referentiel(canonique)
        return BaseController.render(
            "referentiel_import/rapport.html",
            context={
                "rapport": rapport,
                "fichier": saved.original_name,
                "chemin": saved.path,
                "total": sum(rapport.inseres.values()),
            },
            request=request,
        )
