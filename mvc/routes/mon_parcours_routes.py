# pyright: strict
"""Routes de l'espace élève « Mon parcours » (lecture seule).

Protégées par la permission `espace_eleve.voir` (garde posée par `guard_prefix`
dans mvc/routes/__init__.py) : réservées au rôle `eleve`.
"""
from core.http.router import Router
from mvc.controllers.mon_parcours_controller import MonParcoursController
from mvc.controllers.passer_qcm_controller import PasserQcmController


def register_mon_parcours_routes(router: Router) -> None:
    with router.group("/mon-parcours") as g:
        g.add("GET", "", MonParcoursController.index, name="mon_parcours-index")
        g.add("GET", "/qcm/{id}", PasserQcmController.show, name="mon_parcours-qcm")
        g.add("POST", "/qcm/{id}", PasserQcmController.submit, name="mon_parcours-qcm-submit")
