# pyright: strict
"""Routes du contrôleur AuthController (ADR-068)."""
from core.http.router import Router
from mvc.controllers.auth_controller import AuthController


def register_auth_routes(router: Router) -> None:
    # Login public (accessible sans authentification) ; logout protégé.
    router.add("GET", "/login", AuthController.login_form, public=True, name="auth-login_form")
    router.add("POST", "/login", AuthController.login, public=True, name="auth-login")
    # Second facteur (MFA, ADR-015) : public car l'utilisateur n'est pas encore connecté.
    router.add("GET", "/login/mfa", AuthController.mfa_form, public=True, name="auth-mfa_form")
    router.add("POST", "/login/mfa", AuthController.mfa_verify, public=True, name="auth-mfa_verify")
    router.add("POST", "/logout", AuthController.logout, name="auth-logout")
