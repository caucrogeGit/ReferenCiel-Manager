# pyright: strict
"""Routes du contrôleur AuthController (ADR-068)."""
from core.http.router import Router
from mvc.controllers.auth_controller import AuthController


def register_auth_routes(router: Router) -> None:
    # Login public (accessible sans authentification) ; logout protégé.
    router.add("GET", "/login", AuthController.login_form, public=True, name="auth-login_form")
    router.add("POST", "/login", AuthController.login, public=True, name="auth-login")
    router.add("POST", "/logout", AuthController.logout, name="auth-logout")
