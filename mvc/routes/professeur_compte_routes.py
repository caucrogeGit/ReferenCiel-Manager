# pyright: strict
"""Routes de gestion des comptes professeurs (socle admin).

Sous le préfixe `/professeur` → gardées par `socle.gerer` (`guard_prefix`,
mvc/routes/__init__.py). Réservées à l'admin.
"""
from core.http.router import Router
from mvc.controllers.professeur_compte_controller import ProfesseurCompteController


def register_professeur_compte_routes(router: Router) -> None:
    with router.group("/professeur/comptes") as g:
        g.add("GET", "", ProfesseurCompteController.index, name="professeur_compte-index")
        g.add("POST", "/create", ProfesseurCompteController.create, name="professeur_compte-create")
