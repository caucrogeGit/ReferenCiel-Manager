# pyright: strict
"""Routes de l'espace élève « Mon sequence » (lecture seule).

Protégées par la permission `espace_eleve.voir` (garde posée par `guard_prefix`
dans mvc/routes/__init__.py) : réservées au rôle `eleve`.
"""
from core.http.router import Router
from mvc.controllers.checklist_eleve_controller import ChecklistEleveController
from mvc.controllers.depot_eleve_saisie_controller import DepotEleveSaisieController
from mvc.controllers.ma_sequence_controller import MaSequenceController
from mvc.controllers.passer_qcm_controller import PasserQcmController


def register_ma_sequence_routes(router: Router) -> None:
    with router.group("/ma-sequence") as g:
        g.add("GET", "", MaSequenceController.index, name="ma_sequence-index")
        g.add("GET", "/qcm/{id}", PasserQcmController.show, name="ma_sequence-qcm")
        g.add("POST", "/qcm/{id}", PasserQcmController.submit, name="ma_sequence-qcm-submit")
        g.add("GET", "/checklist/{id}", ChecklistEleveController.show, name="ma_sequence-checklist")
        g.add("POST", "/checklist/{id}", ChecklistEleveController.submit, name="ma_sequence-checklist-submit")
        g.add("GET", "/depot/{id}", DepotEleveSaisieController.show, name="ma_sequence-depot")
        g.add("POST", "/depot/{id}", DepotEleveSaisieController.submit, name="ma_sequence-depot-submit")
