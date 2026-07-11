# pyright: strict
"""Réinitialisation de mot de passe (ADR-013 T1).

Flux public : **demande** (`/password/forgot`) → un jeton est créé (cœur
`create_password_reset_token`), persisté (hash) et un lien est proposé → **reset**
(`/password/reset`) → le cœur vérifie le jeton et produit un nouveau hash
(`reset_password_with_token`, qui applique aussi la politique de mot de passe).

Anti-énumération : la demande renvoie un message **générique** quel que soit
l'existence du compte. Faute de mailer configuré, le lien de reset est affiché à
l'écran **uniquement si le compte existe** (compromis de développement, ADR-013).
Routes publiques mais protégées CSRF (défaut Forge) : comme `login_form`, chaque
rendu **garantit une session** (donc un `csrf_token`) pour un visiteur anonyme.
"""
from __future__ import annotations

from typing import Any

from core.auth.exceptions import InvalidNewPasswordError
from core.auth.reset import create_password_reset_token, reset_password_with_token
from core.http.request import Request
from core.http.response import Response
from core.mvc.controller import BaseController
from core.security.cookies import set_session_cookie
from core.security.session import get_session, get_session_id
from core.sessions.manager import get_session_store

from mvc.models.password_reset_model import (
    appliquer_reset,
    enregistrer_token,
    get_token_record,
    get_user_by_email,
)

_RESET_MINUTES = 30
_MESSAGE_GENERIQUE = (
    "Si un compte existe pour cette adresse, un lien de réinitialisation a été généré."
)


def _render_public(
    request: Request, template: str, context: dict[str, Any], status: int = 200
) -> Response:
    """Rendu d'une page publique en garantissant une session + un `csrf_token`.

    Reproduit le pattern de `AuthController.login_form` : un visiteur anonyme n'a pas
    encore de session, donc pas de jeton CSRF ; on en crée une et on pose le cookie.
    """
    session_id = get_session_id(request)
    if not session_id or get_session(session_id) is None:
        session_id = get_session_store().create()
    session = get_session(session_id) or {}
    enriched = {**context, "csrf_token": session.get("csrf_token", "")}
    response = BaseController.render(template, status=status, context=enriched)
    set_session_cookie(response, session_id)
    return response


class PasswordResetController:
    @staticmethod
    def forgot_form(request: Request) -> Response:
        """Formulaire de demande (`GET /password/forgot`)."""
        return _render_public(request, "app/password/forgot.html", {})

    @staticmethod
    def forgot(request: Request) -> Response:
        """Ouvre une demande de reset (`POST /password/forgot`)."""
        email = request.form("email", "").strip()
        user = get_user_by_email(email) if email else None
        lien: str | None = None
        if user is not None and user.get("is_active"):
            raw_token, token = create_password_reset_token(int(user["id"]), _RESET_MINUTES)
            enregistrer_token(token)
            lien = f"/password/reset?token={raw_token}"
        return _render_public(
            request, "app/password/forgot.html", {"message": _MESSAGE_GENERIQUE, "lien": lien}
        )

    @staticmethod
    def reset_form(request: Request) -> Response:
        """Formulaire de nouveau mot de passe (`GET /password/reset?token=…`)."""
        return _render_public(
            request, "app/password/reset.html", {"token": request.query("token", ""), "erreurs": []}
        )

    @staticmethod
    def reset(request: Request) -> Response:
        """Applique le nouveau mot de passe (`POST /password/reset`)."""
        token = request.form("token", "")
        password = request.form("password", "")
        password2 = request.form("password_confirmation", "")

        erreurs: list[str] = []
        if not token:
            erreurs.append("Jeton de réinitialisation manquant.")
        if password != password2:
            erreurs.append("Les deux mots de passe ne correspondent pas.")

        if not erreurs:
            record = get_token_record(token)
            if record is None:
                erreurs.append("Lien invalide ou expiré. Refaites une demande.")
            else:
                try:
                    resultat = reset_password_with_token(token, record, password)
                except InvalidNewPasswordError as exc:
                    erreurs.append(str(exc))
                else:
                    if resultat is None:
                        erreurs.append("Lien invalide, expiré ou déjà utilisé. Refaites une demande.")
                    else:
                        appliquer_reset(
                            resultat.user_id,
                            resultat.password_hash,
                            resultat.used_at,
                            record["token_hash"],
                        )
                        return BaseController.redirect_with_flash(
                            request,
                            "/login",
                            "Mot de passe réinitialisé. Vous pouvez vous connecter.",
                            "success",
                        )

        return _render_public(
            request, "app/password/reset.html", {"token": token, "erreurs": erreurs}, status=422
        )
