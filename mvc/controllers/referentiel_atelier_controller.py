# pyright: strict
"""Atelier référentiel (ADR-018) : vue cohérente d'un référentiel dans son ensemble.

Interface principale de gestion d'un référentiel, en remplacement des CRUD plats
éclatés. Consultation en Phase 1 : sélection d'un référentiel puis affichage de
son arbre complet (maître-détail). L'autorité de construction reste le JSON
canonique (ADR-003) ; les CRUD par entité deviennent une surface d'admin bas niveau.
"""
from core.http.request import Request
from core.http.response import Response
from core.mvc.controller.base_controller import BaseController

from mvc.models.referentiel_atelier_model import get_arbre, get_referentiel, list_referentiels


class ReferentielAtelierController(BaseController):

    @staticmethod
    def _parse_id(raw: object) -> "int | None":
        try:
            return int(raw)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            return None

    @staticmethod
    def index(request: Request) -> Response:
        """Sélection d'un référentiel (liste des référentiels chargés)."""
        return BaseController.render(
            "app/referentiel_atelier/index.html",
            context={"referentiels": list_referentiels()},
            request=request,
        )

    @staticmethod
    def atelier(request: Request) -> Response:
        """Atelier d'un référentiel : son arbre complet en maître-détail."""
        ref_id = ReferentielAtelierController._parse_id(request.route("id"))
        if ref_id is None:
            return BaseController.not_found()
        ref = get_referentiel(ref_id)
        if ref is None:
            return BaseController.not_found()
        return BaseController.render(
            "app/referentiel_atelier/atelier.html",
            context={"ref": ref, "arbre": get_arbre(ref_id)},
            request=request,
        )
