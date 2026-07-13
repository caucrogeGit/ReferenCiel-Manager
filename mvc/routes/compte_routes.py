# pyright: strict
"""Routes de l'espace « Compte » — profil, préférences, aide (self-service).

Pages personnelles du compte connecté, atteintes depuis le menu profil. Protégées
par la seule auth Forge (session requise) ; hors des préfixes gardés RBAC (chacun
consulte SON compte). Chemins racine, dans le style de /mes-classes, /suivi.
"""
from core.http.router import Router

from mvc.controllers.compte_controller import CompteController


def register_compte_routes(router: Router) -> None:
    with router.group("/profil") as g:
        g.add("GET", "", CompteController.profil, name="compte-profil")
    with router.group("/preferences") as g:
        g.add("GET", "", CompteController.preferences, name="compte-preferences")
    with router.group("/a-propos") as g:
        g.add("GET", "", CompteController.a_propos, name="compte-a_propos")
