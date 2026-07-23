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
)
from mvc.models.seance_connaissance_model import savoirs_par_seance_de_sequence
from mvc.models.sequence_model import get_sequence_by_id, recalculer_statut
from mvc.models.referentiel_atelier_model import list_referentiels
from mvc.models.savoir_libre_model import (
    get_savoirs_libres,
    ajouter_savoir_libre,
    get_savoir_libre,
    supprimer_savoir_libre,
)
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
            # Savoirs libres (ADR-030) : le professeur les saisit lui-même.
            "savoirs_libres": get_savoirs_libres(sequence_id),
            "competences": [],
            "liens": {},
            "competence_id": None,
            "niveaux": _NIVEAUX,
            "statuts": _STATUTS,
        }
    # ADR-037 : les savoirs vivent sur les SÉANCES ; la séquence n'en montre
    # qu'une SYNTHÈSE dérivée, groupée par compétence avec la séance d'origine.
    return {
        "sequence_id": sequence_id,
        "ref_absent": False,
        "synthese": savoirs_par_seance_de_sequence(sequence_id),
        "statut_labels": STATUT_LABELS,
    }


class SequenceConnaissanceController(BaseController):

    @staticmethod
    def _rendre(request: Request, sequence_id: int, competence_id, message_garde=None) -> Response:
        if not est_htmx(request):
            return BaseController.redirect(
                f"/sequence/editeur/{sequence_id}?etape=cadre", request=request
            )
        context = contexte_connaissances(sequence_id, competence_id)
        if message_garde:
            context["message_garde"] = message_garde
        return BaseController.render(
            "app/sequence/_connaissances.html",
            context=context,
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
            # Un référentiel fraîchement rattaché exige des connaissances : la
            # séquence peut redescendre en brouillon (ADR-034).
            recalculer_statut(sequence_id)
        return SequenceConnaissanceController._rendre(request, sequence_id, None)

    # ── Savoirs libres (séquence hors référentiel, ADR-030) ──────────────────
    #
    # Saisie libre par le professeur, comme les indicateurs de réussite. Écriture
    # ciblée d'un seul savoir, puis retour du fragment #connaissances-sequence.

    @staticmethod
    def ajouter_savoir(request: Request) -> Response:
        sequence_id = _parse_id(request.route("id"))
        if sequence_id is None or get_sequence_by_id(sequence_id) is None:
            return BaseController.not_found()
        libelle = (request.form("libelle", "") or "").strip()
        if libelle:
            ajouter_savoir_libre(sequence_id, libelle)
        return SequenceConnaissanceController._rendre(request, sequence_id, None)

    @staticmethod
    def supprimer_savoir(request: Request) -> Response:
        savoir_id = _parse_id(request.route("sid"))
        if savoir_id is None:
            return BaseController.not_found()
        savoir = get_savoir_libre(savoir_id)
        if savoir is None:
            return BaseController.not_found()
        sequence_id = savoir["sequence_id"]
        supprimer_savoir_libre(savoir_id)
        return SequenceConnaissanceController._rendre(request, sequence_id, None)
