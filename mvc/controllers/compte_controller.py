# pyright: strict
"""Espace « Compte » du self-service utilisateur — profil, préférences, aide.

Pages personnelles du compte **connecté**, accessibles depuis le menu profil de la
barre de navigation. Protégées par la seule auth Forge (session requise) : chacun
consulte SON compte ; pas de permission de domaine. La gestion sensible (mot de passe,
MFA) reste dans l'espace « Sécurité » (ADR-014/014) — on y renvoie, on ne la duplique
pas.
"""
from __future__ import annotations

import config
from core.auth.session import get_authenticated_user_id
from core.database.db import fetch_one
from core.http.request import Request
from core.http.response import Response
from core.mvc.controller import BaseController
from forge_mvc_rbac import get_request_roles

#: Libellés d'affichage des rôles du contrat (mvc/security/rbac.json).
_ROLE_LABELS = {
    "admin": "Administrateur",
    "professeur": "Professeur",
    "eleve": "Élève",
}


def _role_libelles(roles: list[str]) -> list[str]:
    """Traduit les slugs de rôle en libellés lisibles (slug brut en repli)."""
    return [_ROLE_LABELS.get(role, role) for role in roles]


class CompteController:
    @staticmethod
    def profil(request: Request) -> Response:
        """Fiche du compte connecté (`GET /profil`) : email, rôle(s), statut."""
        user_id = get_authenticated_user_id(request)
        if user_id is None:
            return BaseController.redirect("/login")
        row = fetch_one("SELECT email, is_active FROM users WHERE id = ?", (user_id,))
        email = str(row["email"]) if row is not None else ""
        actif = bool(row["is_active"]) if row is not None else False
        return BaseController.render(
            "app/compte/profil.html",
            context={
                "email": email,
                "actif": actif,
                "roles": _role_libelles(get_request_roles(request)),
            },
            request=request,
        )

    @staticmethod
    def preferences(request: Request) -> Response:
        """Préférences du compte (`GET /preferences`). Aucune option pour l'instant."""
        if get_authenticated_user_id(request) is None:
            return BaseController.redirect("/login")
        return BaseController.render(
            "app/compte/preferences.html", context={}, request=request
        )

    @staticmethod
    def a_propos(request: Request) -> Response:
        """À propos de l'application (`GET /a-propos`) : informations et version."""
        if get_authenticated_user_id(request) is None:
            return BaseController.redirect("/login")
        return BaseController.render(
            "app/compte/a_propos.html",
            context={"version": config.APP_VERSION},
            request=request,
        )
