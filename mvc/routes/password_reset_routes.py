# pyright: strict
"""Routes de la réinitialisation de mot de passe (ADR-014 T1).

Publiques (un utilisateur non connecté doit pouvoir réinitialiser), mais protégées
CSRF sur les POST (défaut Forge). Aucune permission RBAC (hors des préfixes gardés).
"""
from core.http.router import Router

from mvc.controllers.password_reset_controller import PasswordResetController


def register_password_reset_routes(router: Router) -> None:
    router.add(
        "GET", "/password/forgot", PasswordResetController.forgot_form,
        public=True, name="password-forgot_form",
    )
    router.add(
        "POST", "/password/forgot", PasswordResetController.forgot,
        public=True, name="password-forgot",
    )
    router.add(
        "GET", "/password/reset", PasswordResetController.reset_form,
        public=True, name="password-reset_form",
    )
    router.add(
        "POST", "/password/reset", PasswordResetController.reset,
        public=True, name="password-reset",
    )
