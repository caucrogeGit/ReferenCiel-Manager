# pyright: strict
"""Routes du bilan élève (ticket 21).

Protégées par la permission `execution.gerer` (garde posée par `guard_prefix` dans
mvc/routes/__init__.py) : rôles `admin` et `professeur`. L'auteur d'un bilan est
déduit du compte connecté (`professeur.UserId`).
"""
from core.http.router import Router

from mvc.controllers.bilan_eleve_controller import BilanEleveController


def register_bilan_eleve_routes(router: Router) -> None:
    with router.group("/bilan") as g:
        g.add("GET", "", BilanEleveController.index, name="bilan-index")
        g.add("GET", "/new", BilanEleveController.new, name="bilan-new")
        g.add("POST", "/create", BilanEleveController.create, name="bilan-create")
        g.add("GET", "/show/{id}", BilanEleveController.show, name="bilan-show")
