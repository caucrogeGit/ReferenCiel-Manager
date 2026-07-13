# pyright: strict
"""Routes de l'espace « Sécurité » — MFA self-service (ADR-015).

Protégées par la seule auth Forge (session requise) : chaque utilisateur connecté
gère SA propre MFA. Pas de permission de domaine (hors des préfixes gardés). POST
protégés CSRF (défaut Forge).
"""
from core.http.router import Router

from mvc.controllers.securite_controller import SecuriteController


def register_securite_routes(router: Router) -> None:
    with router.group("/securite") as g:
        g.add("GET", "", SecuriteController.index, name="securite-index")
        g.add("GET", "/activer", SecuriteController.activer, name="securite-activer")
        g.add("POST", "/confirmer", SecuriteController.confirmer, name="securite-confirmer")
        g.add("POST", "/codes/regenerer", SecuriteController.regenerer_codes, name="securite-codes-regenerer")
        g.add("GET", "/desactiver", SecuriteController.desactiver_confirm, name="securite-desactiver_confirm")
        g.add("POST", "/desactiver", SecuriteController.desactiver, name="securite-desactiver")
