"""Édition des connaissances associées d'une séquence (ADR-028).

Maître-détail compétence → connaissances, sur la fiche séquence. Le référentiel
est résolu via le scénario appairé ; sans référentiel, la section est inactive
(cohérent ADR-027). Chaque requête écrit un seul lien puis renvoie le fragment
#connaissances-sequence (ou redirige vers la fiche sans JS).
"""

from core.http.request import Request
from core.http.response import Response
from core.mvc.controller import BaseController

from mvc.helpers.htmx import est_htmx
from mvc.models.sequence_connaissance_model import (
    STATUT_LABELS,
    get_referentiel_id_for_sequence,
    get_scenario_id_for_sequence,
    get_arbre_connaissances,
    get_liens_by_sequence,
    lier,
    delier,
    maj_niveau_cible,
    maj_statut,
)
from mvc.models.sequence_model import get_sequence_by_id
from mvc.models.referentiel_atelier_model import list_referentiels
from mvc.models.scenario_editeur_model import (
    enregistrer_referentiel as _rattacher_referentiel,
    paire_est_finalisee,
)

_NIVEAUX = [("", "—"), ("1", "1"), ("2", "2"), ("3", "3"), ("4", "4")]
_STATUTS = [("", "—")] + [(v, STATUT_LABELS[v]) for v in STATUT_LABELS]


def _parse_id(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _query(request, name, default=""):
    values = request.params.get(name, [default])
    return values[0] if values else default


def contexte_connaissances(sequence_id, competence_id=None):
    """Contexte du bloc connaissances : arbre, liens, compétence active.

    Réutilisé par la fiche séquence (show) et par les fragments HTMX.
    """
    ref_id = get_referentiel_id_for_sequence(sequence_id)
    if ref_id is None:
        # Pas de référentiel : on propose d'en rattacher un (via le scénario
        # appairé), SAUF si la paire est finalisée — le référentiel est alors
        # verrouillé des deux côtés (retour terrain).
        scenario_id = get_scenario_id_for_sequence(sequence_id)
        verrouille = paire_est_finalisee(int(scenario_id)) if scenario_id is not None else False
        return {
            "sequence_id": sequence_id,
            "ref_absent": True,
            "referentiel_verrouille": verrouille,
            "referentiels": [] if verrouille else list_referentiels(),
            "competences": [],
            "liens": {},
            "competence_id": None,
            "niveaux": _NIVEAUX,
            "statuts": _STATUTS,
        }
    competences = get_arbre_connaissances(ref_id)
    if competence_id is None and competences:
        competence_id = competences[0]["Id"]
    return {
        "sequence_id": sequence_id,
        "ref_absent": False,
        "competences": competences,
        "liens": get_liens_by_sequence(sequence_id),
        "competence_id": competence_id,
        "niveaux": _NIVEAUX,
        "statuts": _STATUTS,
    }


class SequenceConnaissanceController(BaseController):

    @staticmethod
    def _rendre(request: Request, sequence_id: int, competence_id) -> Response:
        if not est_htmx(request):
            return BaseController.redirect(
                f"/sequence/editeur/{sequence_id}?etape=connaissances", request=request
            )
        return BaseController.render(
            "app/sequence/_connaissances.html",
            context=contexte_connaissances(sequence_id, competence_id),
            request=request,
        )

    @staticmethod
    def afficher(request: Request) -> Response:
        sequence_id = _parse_id(request.route("id"))
        if sequence_id is None or get_sequence_by_id(sequence_id) is None:
            return BaseController.not_found()
        competence_id = _parse_id(_query(request, "competence"))
        return SequenceConnaissanceController._rendre(request, sequence_id, competence_id)

    @staticmethod
    def rattacher_referentiel(request: Request) -> Response:
        """Rattache un référentiel au scénario appairé, depuis la séquence, pour
        débloquer la sélection des savoirs (retour terrain / ADR-027)."""
        sequence_id = _parse_id(request.route("id"))
        if sequence_id is None or get_sequence_by_id(sequence_id) is None:
            return BaseController.not_found()
        referentiel_id = _parse_id(request.form("referentiel_id", ""))
        scenario_id = get_scenario_id_for_sequence(sequence_id)
        # Verrou : on ne change pas le référentiel d'une paire finalisée.
        if (
            referentiel_id is not None
            and scenario_id is not None
            and not paire_est_finalisee(int(scenario_id))
        ):
            _rattacher_referentiel(int(scenario_id), referentiel_id)
        return SequenceConnaissanceController._rendre(request, sequence_id, None)

    @staticmethod
    def basculer(request: Request) -> Response:
        sequence_id = _parse_id(request.route("id"))
        if sequence_id is None or get_sequence_by_id(sequence_id) is None:
            return BaseController.not_found()
        connaissance_id = _parse_id(request.form("connaissance", ""))
        competence_id = _parse_id(request.form("competence", ""))
        if connaissance_id is not None:
            liens = get_liens_by_sequence(sequence_id)
            if connaissance_id in liens:
                delier(sequence_id, connaissance_id)
            else:
                lier(sequence_id, connaissance_id)
        return SequenceConnaissanceController._rendre(request, sequence_id, competence_id)

    @staticmethod
    def niveau(request: Request) -> Response:
        sequence_id = _parse_id(request.route("id"))
        if sequence_id is None or get_sequence_by_id(sequence_id) is None:
            return BaseController.not_found()
        connaissance_id = _parse_id(request.form("connaissance", ""))
        competence_id = _parse_id(request.form("competence", ""))
        niveau = _parse_id(request.form("niveau", ""))  # None si vide → efface
        if connaissance_id is not None:
            maj_niveau_cible(sequence_id, connaissance_id, niveau)
        return SequenceConnaissanceController._rendre(request, sequence_id, competence_id)

    @staticmethod
    def statut(request: Request) -> Response:
        sequence_id = _parse_id(request.route("id"))
        if sequence_id is None or get_sequence_by_id(sequence_id) is None:
            return BaseController.not_found()
        connaissance_id = _parse_id(request.form("connaissance", ""))
        competence_id = _parse_id(request.form("competence", ""))
        statut_val = (request.form("statut", "") or "").strip()
        if statut_val not in STATUT_LABELS:
            statut_val = None  # valeur vide ou inconnue → efface
        if connaissance_id is not None:
            maj_statut(sequence_id, connaissance_id, statut_val)
        return SequenceConnaissanceController._rendre(request, sequence_id, competence_id)
