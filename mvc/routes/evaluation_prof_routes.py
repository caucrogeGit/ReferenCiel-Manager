# pyright: strict
"""Routes de l'évaluation professeur (boucle de progression).

Sous le préfixe `/evaluation` → gardées par `execution.gerer` (`guard_prefix`,
mvc/routes/__init__.py). Réservées au professeur et à l'admin.
"""
from core.http.router import Router
from mvc.controllers.evaluation_prof_controller import EvaluationProfController


def register_evaluation_prof_routes(router: Router) -> None:
    with router.group("/evaluation") as g:
        g.add("GET", "/progression/{id}", EvaluationProfController.progression, name="evaluation-progression")
        g.add("POST", "/palier/{id}/statut", EvaluationProfController.set_statut, name="evaluation-palier-statut")
        g.add("GET", "/checklist/{id}", EvaluationProfController.checklist, name="evaluation-checklist")
        g.add("POST", "/checklist/{id}", EvaluationProfController.coche, name="evaluation-checklist-coche")
