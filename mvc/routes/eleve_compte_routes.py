# pyright: strict
"""Routes de gestion des comptes élèves (socle admin).

Sous le préfixe `/eleve` → gardées par `socle.gerer` (`guard_prefix`,
mvc/routes/__init__.py). Réservées à l'admin.
"""
from core.http.router import Router
from mvc.controllers.eleve_compte_controller import EleveCompteController


def register_eleve_compte_routes(router: Router) -> None:
    with router.group("/eleve/comptes") as g:
        g.add("GET", "", EleveCompteController.index, name="eleve_compte-index")
        g.add("POST", "/create", EleveCompteController.create, name="eleve_compte-create")
