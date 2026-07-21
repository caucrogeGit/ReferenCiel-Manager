# pyright: strict
"""Suivi professeur (ADR-033) : tableau de bord **multi-entrées** de la progression.

`/suivi` est une page à **tuiles**, chacune une lentille du même graphe de suivi :
- par **classe** : classe → élèves → avancement par séquence ;
- par **séquence** : séquence → classes qui l'utilisent → élèves.
Les lentilles convergent (à terme) vers la feuille de positionnement. Lecture
seule pour l'instant. Route protégée.
"""
from __future__ import annotations

from core.auth.session import get_authenticated_user_id
from core.http.request import Request
from core.http.response import Response
from core.mvc.controller import BaseController

from mvc.models.mes_classes_model import get_professeur_by_user
from mvc.models.suivi_model import (
    compter_lentilles,
    get_classe,
    list_classes,
    suivi_eleves,
    list_sequences,
    get_sequence_suivi,
    classes_pour_sequence,
)


def _professeur_id(request: Request) -> "int | None":
    user_id = get_authenticated_user_id(request)
    professeur = get_professeur_by_user(user_id) if user_id is not None else None
    return int(professeur["id"]) if professeur is not None else None


class SuiviController:
    @staticmethod
    def index(request: Request) -> Response:
        """Tableau de bord à tuiles (`GET /suivi`)."""
        pid = _professeur_id(request)
        compteurs = compter_lentilles(pid) if pid is not None else {"nb_classes": 0, "nb_sequences": 0}
        return BaseController.render(
            "app/suivi/dashboard.html", context={"compteurs": compteurs}, request=request
        )

    # ── Lentille « par classe » ──────────────────────────────────────────────

    @staticmethod
    def classes(request: Request) -> Response:
        """Liste des classes du professeur (`GET /suivi/classes`)."""
        pid = _professeur_id(request)
        classes = list_classes(pid) if pid is not None else []
        return BaseController.render(
            "app/suivi/classes.html", context={"classes": classes}, request=request
        )

    @staticmethod
    def classe(request: Request) -> Response:
        """Détail d'une classe : élèves et avancement (`GET /suivi/classe/<id>`)."""
        classe_id = int(request.route("id") or "0")
        classe = get_classe(classe_id)
        if classe is None:
            return BaseController.not_found()
        return BaseController.render(
            "app/suivi/classe.html",
            context={"classe": classe, "eleves": suivi_eleves(classe_id)},
            request=request,
        )

    # ── Lentille « par séquence » ────────────────────────────────────────────

    @staticmethod
    def sequences(request: Request) -> Response:
        """Liste des séquences suivies (`GET /suivi/sequences`)."""
        pid = _professeur_id(request)
        sequences = list_sequences(pid) if pid is not None else []
        return BaseController.render(
            "app/suivi/sequences.html", context={"sequences": sequences}, request=request
        )

    @staticmethod
    def sequence(request: Request) -> Response:
        """Détail d'une séquence : classes qui l'utilisent (`GET /suivi/sequence/<id>`)."""
        pid = _professeur_id(request)
        sequence_id = int(request.route("id") or "0")
        sequence = get_sequence_suivi(sequence_id)
        if sequence is None:
            return BaseController.not_found()
        classes = classes_pour_sequence(sequence_id, pid) if pid is not None else []
        return BaseController.render(
            "app/suivi/sequence.html",
            context={"sequence": sequence, "classes": classes},
            request=request,
        )
