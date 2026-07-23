"""Éditeur tunnel de la séance (ADR-032, miroir de l'éditeur séquence).

On ne quitte jamais la page : navigation d'étape et auto-save via HTMX (toast
hors-bande). L'étape « Compétences observées » propose une sélection maître-détail
PARMI la liaison du scénario appairé (cascade sans double saisie).
"""

from core.http.request import Request
from core.http.response import Response
from core.mvc.controller import BaseController

from mvc.helpers.htmx import est_htmx
from mvc.services.seance_tunnel import borner_etape, navigation, parse_id, steps
from mvc.models.seance_model import (
    add_seance,
    get_seance_by_id,
    feuilles_famille,
    motif_blocage_suppression,
    prochain_ordre,
    update_fiche,
)
from mvc.models.sequence_model import (
    get_sequence_by_id,
    recalculer_statut as recalculer_statut_sequence,
)
from mvc.models.scenario_editeur_model import get_scenario
from mvc.models.referentiel_atelier_model import get_referentiel
from mvc.models.seance_competence_model import (
    ROLE_LABELS,
    get_scenario_id_for_seance,
    get_arbre_liaison,
    get_competences_observees,
    get_criteres_observes,
    synchroniser_observation,
    maj_role,
    basculer_critere,
)
from mvc.models.element_seance_model import (
    TYPES,
    TYPE_LABELS,
    get_elements,
    get_element,
    ajouter as ajouter_element_db,
    maj as maj_element_db,
    supprimer as supprimer_element_db,
    deplacer as deplacer_element_db,
)
from mvc.controllers.seance_connaissance_controller import contexte_savoirs
from mvc.models.seance_connaissance_model import get_liens_by_seance
from mvc.services.sequence_tunnel import nb_savoirs_ouvrants
from mvc.models.qcm_model import qcms_pour_seance
from mvc.models.checklist_model import checklists_pour_seance

_ROLES = [(v, ROLE_LABELS[v]) for v in ROLE_LABELS]
_TYPES = [(t, TYPE_LABELS[t]) for t in TYPES]


def _query(request, name, default=""):
    values = request.params.get(name, [default])
    return values[0] if values else default


def contexte_competences(seance_id, competence_id=None):
    """Contexte de l'étape Compétences observées (maître-détail scopé scénario)."""
    scenario_id = get_scenario_id_for_seance(seance_id)
    groupes = get_arbre_liaison(scenario_id) if scenario_id is not None else []
    if not groupes:
        return {
            "seance_id": seance_id,
            "liaison_absente": True,
            "groupes": [],
            "competences_observees": {},
            "criteres_observes": set(),
            "competence_id": None,
            "roles": _ROLES,
        }
    if competence_id is None:
        competence_id = groupes[0]["Id"]
    return {
        "seance_id": seance_id,
        "liaison_absente": False,
        "groupes": groupes,
        "competences_observees": get_competences_observees(seance_id),
        "criteres_observes": get_criteres_observes(seance_id),
        "competence_id": competence_id,
        "roles": _ROLES,
    }


def contexte_deroule(seance_id):
    """Contexte de l'étape Déroulé (liste ordonnée des éléments + types).

    qcms/checklists : objets de la séance référençables par les éléments de
    type « qcm »/« checklist » (ADR-035).
    """
    return {
        "seance_id": seance_id,
        "elements": get_elements(seance_id),
        "types": _TYPES,
        "type_labels": TYPE_LABELS,
        "qcms": qcms_pour_seance(seance_id),
        "checklists": checklists_pour_seance(seance_id),
    }


def _nb_savoirs_ouvrants_de_seance(seance: dict) -> int:
    """Savoirs OUVRANTS de la séance (ADR-037) : conditionnent l'étape Savoirs
    et la publication de la séquence. La nature vient de la séquence (héritée)."""
    return nb_savoirs_ouvrants(
        list(get_liens_by_seance(seance["Id"]).values()),
        seance.get("sequence_nature"),
    )


def _contexte_editeur(seance: dict, etape: str) -> dict:
    """Contexte complet de l'éditeur (coquille + étape active)."""
    sid = seance["Id"]
    nb_competences = len(get_competences_observees(sid))
    nb_elements = len(get_elements(sid))
    context = {
        "seance": seance,
        "base_url": f"/seance/editeur/{sid}",
        "steps": steps(seance, _nb_savoirs_ouvrants_de_seance(seance), nb_competences, nb_elements),
        # Arbre de la famille (ADR-029) : scénario de la paire et séances sœurs.
        "seances_soeurs": feuilles_famille(seance["sequence_id"], seance.get("sequence_nature")),
        "scenario_lie": (scenario_lie := (
            get_scenario(int(scid))
            if (scid := get_scenario_id_for_seance(sid)) is not None
            else None
        )),
        "referentiel_actuel": (
            get_referentiel(int(scenario_lie["referentiel_id"]))
            if scenario_lie and scenario_lie.get("referentiel_id") else None
        ),
    }
    context.update(navigation(etape))
    context.update(contexte_competences(sid))
    context.update(contexte_deroule(sid))
    # Étape Gestion (ADR-038) : motif humain bloquant la suppression, ou None.
    context["motif_suppression_seance"] = motif_blocage_suppression(sid)
    if etape == "savoirs":
        # Contexte de l'étape Savoirs associés (arbre du référentiel, liens,
        # statuts par nature) : indispensable au rendu PLEINE PAGE de l'étape
        # (le fragment HTMX /seance/{id}/savoirs le reconstruit seul). Chargé en
        # dernier et seulement pour cette étape : son competence_id (aucune
        # sélection par défaut) écraserait celui du maître-détail Compétences.
        context.update(contexte_savoirs(sid))
    return context


class SeanceEditeurController(BaseController):

    @staticmethod
    def nouveau(request: Request) -> Response:
        """Création inline depuis la liste (même motif que séquences et
        scénarios) : titre et séquence obligatoires, ordre calculé en fin de
        séquence, puis ouverture directe de l'éditeur tunnel. Le reste de la
        fiche se remplit dans le tunnel."""
        titre = (request.form("titre", "") or "").strip()
        sequence_id = parse_id(request.form("sequence_id", ""))
        if not titre:
            return BaseController.redirect(
                "/sequence", request=request,
                flash="Le titre est obligatoire.", level="success",
            )
        sequence = get_sequence_by_id(sequence_id) if sequence_id is not None else None
        if sequence_id is None or sequence is None:
            return BaseController.redirect(
                "/sequence", request=request,
                flash="Choisissez une séquence de rattachement.", level="success",
            )
        # Une séance se lie dès que la séquence est FINALISÉE (ADR-034) : la
        # garde serveur double le filtrage du sélecteur. Une séquence qui porte
        # DÉJÀ des séances reste extensible même retombée en brouillon (l'arbre
        # « Famille pédagogique » propose l'ajout en continu).
        if sequence.get("Statut") not in ("finalise", "publie", "attribue") and prochain_ordre(sequence_id) == 1:
            return BaseController.redirect(
                "/sequence", request=request,
                flash="Choisissez une séquence finalisée de rattachement.", level="success",
            )
        sid = add_seance({
            "ordre": prochain_ordre(sequence_id),
            "titre": titre,
            "theme": None,
            "production_attendue": None,
            "objectif_operationnel": None,
            "consigne_generale": None,
            "duree_estimee_minutes": None,
            "prerequis": None,
            "modalite_pedagogique": None,
            "condition_realisation": None,
            "condition_validation": None,
            "remediation": None,
            "sequence_id": sequence_id,
        })
        # La première séance liée fait passer la séquence en « publie » (ADR-034).
        recalculer_statut_sequence(sequence_id)
        return BaseController.redirect(f"/seance/editeur/{sid}")

    @staticmethod
    def editeur(request: Request) -> Response:
        sid = parse_id(request.route("id"))
        if sid is None:
            return BaseController.not_found()
        seance = get_seance_by_id(sid)
        if seance is None:
            return BaseController.not_found()
        # Auto-réparation du statut séquence (dérivé persisté) avant lecture :
        # la fiche séance embarque sequence_statut, il doit être à jour.
        recalculer_statut_sequence(seance["sequence_id"])
        seance = get_seance_by_id(sid)
        if seance is None:
            return BaseController.not_found()
        etape = borner_etape(request.query("etape", "fiche"))
        context = _contexte_editeur(seance, etape)
        template = "app/seance_editeur/_corps.html" if est_htmx(request) else "app/seance_editeur/editeur.html"
        return BaseController.render(template, context=context, request=request)

    @staticmethod
    def enregistrer_fiche(request: Request) -> Response:
        sid = parse_id(request.route("id"))
        if sid is None or get_seance_by_id(sid) is None:
            return BaseController.not_found()
        data = {
            "ordre": parse_id(request.form("ordre", "")) or 1,
            "titre": (request.form("titre", "") or "").strip(),
            "theme": (request.form("theme", "") or "").strip() or None,
            "production_attendue": (request.form("production_attendue", "") or "").strip() or None,
            "objectif_operationnel": (request.form("objectif_operationnel", "") or "").strip() or None,
            "consigne_generale": (request.form("consigne_generale", "") or "").strip() or None,
            "duree_estimee_minutes": parse_id(request.form("duree_estimee_minutes", "")),
            "prerequis": (request.form("prerequis", "") or "").strip() or None,
            "modalite_pedagogique": (request.form("modalite_pedagogique", "") or "").strip() or None,
            "condition_realisation": (request.form("condition_realisation", "") or "").strip() or None,
            "condition_validation": (request.form("condition_validation", "") or "").strip() or None,
            "remediation": (request.form("remediation", "") or "").strip() or None,
        }
        update_fiche(sid, data)
        if est_htmx(request):
            # La séance fraîche alimente les rafraîchissements hors-bande :
            # grand titre de l'en-tête et stepper recalculé, en plus du toast.
            seance_fraiche = get_seance_by_id(sid)
            context = {} if seance_fraiche is None else {
                "seance": seance_fraiche,
                "steps": steps(
                    seance_fraiche,
                    _nb_savoirs_ouvrants_de_seance(seance_fraiche),
                    len(get_competences_observees(sid)),
                    len(get_elements(sid)),
                ),
                "etape": "fiche",
                "base_url": f"/seance/editeur/{sid}",
                # Arbre « Famille pédagogique » hors-bande (titre à jour).
                "arbre_oob": True,
                "seances_soeurs": feuilles_famille(seance_fraiche["sequence_id"], seance_fraiche.get("sequence_nature")),
                "scenario_lie": (scenario_lie := (
                    get_scenario(int(scid))
                    if (scid := get_scenario_id_for_seance(sid)) is not None
                    else None
                )),
                "referentiel_actuel": (
                    get_referentiel(int(scenario_lie["referentiel_id"]))
                    if scenario_lie and scenario_lie.get("referentiel_id") else None
                ),
            }
            return BaseController.render(
                "app/seance_editeur/_sauvegarde_oob.html",
                context=context,
                request=request,
            )
        return BaseController.redirect(f"/seance/editeur/{sid}", request=request)

    # ── Étape Compétences observées (maître-détail, ADR-032 A2) ──────────────

    @staticmethod
    def _contexte_stepper(sid, etape):
        """Stepper recalculé, renvoyé hors-bande avec les fragments : la coche et
        les badges des étapes suivent chaque écriture, sur toutes les sections."""
        seance = get_seance_by_id(sid)
        if seance is None:
            return {}
        return {
            "steps": steps(
                seance,
                _nb_savoirs_ouvrants_de_seance(seance),
                len(get_competences_observees(sid)),
                len(get_elements(sid)),
            ),
            "etape": etape,
            "base_url": f"/seance/editeur/{sid}",
            "stepper_oob": True,
        }

    @staticmethod
    def _rendre_competences(request: Request, sid: int, competence_id) -> Response:
        if not est_htmx(request):
            return BaseController.redirect(
                f"/seance/editeur/{sid}?etape=competences", request=request
            )
        context = contexte_competences(sid, competence_id)
        context.update(SeanceEditeurController._contexte_stepper(sid, "competences"))
        return BaseController.render(
            "app/seance_editeur/_competences.html", context=context, request=request,
        )

    @staticmethod
    def afficher_competences(request: Request) -> Response:
        sid = parse_id(request.route("id"))
        if sid is None or get_seance_by_id(sid) is None:
            return BaseController.not_found()
        competence_id = parse_id(_query(request, "competence"))
        return SeanceEditeurController._rendre_competences(request, sid, competence_id)

    @staticmethod
    def changer_role(request: Request) -> Response:
        sid = parse_id(request.route("id"))
        if sid is None or get_seance_by_id(sid) is None:
            return BaseController.not_found()
        competence_id = parse_id(request.form("competence", ""))
        if competence_id is not None:
            maj_role(sid, competence_id, (request.form("role", "") or "").strip())
        return SeanceEditeurController._rendre_competences(request, sid, competence_id)

    @staticmethod
    def basculer_critere(request: Request) -> Response:
        sid = parse_id(request.route("id"))
        if sid is None or get_seance_by_id(sid) is None:
            return BaseController.not_found()
        competence_id = parse_id(request.form("competence", ""))
        critere_id = parse_id(request.form("critere", ""))
        if critere_id is not None:
            basculer_critere(sid, critere_id)
            # L'observation de la compétence est DÉRIVÉE de ses critères cochés
            # (retour porteur) : synchronisée à chaque bascule.
            if competence_id is not None:
                synchroniser_observation(sid, competence_id)
        return SeanceEditeurController._rendre_competences(request, sid, competence_id)

    # ── Étape Déroulé : éléments ordonnés (ADR-032 phase B) ──────────────────

    @staticmethod
    def _rendre_deroule(request: Request, sid: int) -> Response:
        if not est_htmx(request):
            return BaseController.redirect(f"/seance/editeur/{sid}?etape=deroule", request=request)
        context = contexte_deroule(sid)
        context.update(SeanceEditeurController._contexte_stepper(sid, "deroule"))
        return BaseController.render(
            "app/seance_editeur/_elements.html", context=context, request=request
        )

    @staticmethod
    def _lire_element(request: Request) -> dict:
        return {
            "titre": (request.form("titre", "") or "").strip(),
            "contenu": (request.form("contenu", "") or "").strip() or None,
            "duree": parse_id(request.form("duree_minutes", "")),
            "obligatoire": request.form("obligatoire", "") != "",
            "role": (request.form("role_pedagogique", "") or "").strip() or None,
        }

    @staticmethod
    def ajouter_element(request: Request) -> Response:
        sid = parse_id(request.route("id"))
        if sid is None or get_seance_by_id(sid) is None:
            return BaseController.not_found()
        type_ = (request.form("type", "") or "").strip()
        d = SeanceEditeurController._lire_element(request)
        if type_ in TYPES and d["titre"]:
            ajouter_element_db(sid, type_, d["titre"], d["contenu"], d["duree"], d["obligatoire"], d["role"])
        return SeanceEditeurController._rendre_deroule(request, sid)

    @staticmethod
    def maj_element(request: Request) -> Response:
        eid = parse_id(request.route("eid"))
        if eid is None:
            return BaseController.not_found()
        element = get_element(eid)
        if element is None:
            return BaseController.not_found()
        d = SeanceEditeurController._lire_element(request)
        # Référence QCM/checklist (ADR-035) : selon le type de l'élément, bornée
        # aux objets de la séance (une référence étrangère est ignorée).
        sid = element["seance_id"]
        qcm_id = checklist_id = None
        if element["Type"] == "qcm":
            qcm_id = parse_id(request.form("qcm_id", ""))
            if qcm_id not in {int(q["Id"]) for q in qcms_pour_seance(sid)}:
                qcm_id = None
        elif element["Type"] == "checklist":
            checklist_id = parse_id(request.form("checklist_id", ""))
            if checklist_id not in {int(c["Id"]) for c in checklists_pour_seance(sid)}:
                checklist_id = None
        if d["titre"]:
            maj_element_db(eid, d["titre"], d["contenu"], d["duree"], d["obligatoire"], d["role"],
                           qcm_id=qcm_id, checklist_id=checklist_id)
        return SeanceEditeurController._rendre_deroule(request, sid)

    @staticmethod
    def supprimer_element(request: Request) -> Response:
        eid = parse_id(request.route("eid"))
        if eid is None:
            return BaseController.not_found()
        element = get_element(eid)
        if element is None:
            return BaseController.not_found()
        seance_id = element["seance_id"]
        supprimer_element_db(eid)
        return SeanceEditeurController._rendre_deroule(request, seance_id)

    @staticmethod
    def deplacer_element(request: Request) -> Response:
        eid = parse_id(request.route("eid"))
        if eid is None:
            return BaseController.not_found()
        element = get_element(eid)
        if element is None:
            return BaseController.not_found()
        sens = (request.form("sens", "") or "").strip()
        if sens in ("haut", "bas"):
            deplacer_element_db(eid, sens)
        return SeanceEditeurController._rendre_deroule(request, element["seance_id"])
