"""Éditeur tunnel de la séquence (miroir de l'éditeur scénario).

On ne quitte jamais la page : chaque navigation d'étape régénère le fragment
#tunnel-corps via HTMX ; l'auto-save d'un champ renvoie un toast hors-bande.
Les connaissances associées (ADR-028) sont éditées dans l'étape dédiée, via le
contrôleur SequenceConnaissanceController (routes /sequence/{id}/connaissance/*).
"""

from core.http.request import Request
from core.http.response import Response
from core.mvc.controller import BaseController

from mvc.helpers.htmx import est_htmx
from mvc.services.sequence_tunnel import (
    NATURES,
    ORGANISATIONS,
    borner_etape,
    duree_lisible,
    mode_organisation,
    navigation,
    parse_id,
    steps,
)
from mvc.models.sequence_model import (
    get_sequence_by_id,
    titre_existe_autre as titre_sequence_existe_autre,
    update_identite,
    update_cadre,
    get_niveau_classe_choices,
    get_niveau_choices_pour_referentiel,
    recalculer_statut,
)
from mvc.models.scenario_editeur_model import creer_sequence_et_scenario, get_scenario, titre_existe
from mvc.models.seance_model import (
    duree_cumulee_minutes,
    feuilles_famille,
    prerequis_par_seance,
)
from mvc.models.referentiel_atelier_model import get_referentiel, list_referentiels
from mvc.models.sequence_connaissance_model import (
    get_referentiel_id_for_sequence,
    get_scenario_id_for_sequence,
)
from mvc.controllers.sequence_connaissance_controller import contexte_connaissances


def _contexte_editeur(sequence: dict, etape: str) -> dict:
    """Contexte complet de l'éditeur (coquille + étape active)."""
    sid = sequence["Id"]
    seances = feuilles_famille(sid, sequence.get("Nature"))
    # Rappel du choix fait à la création (étape Titre) : le référentiel vit sur
    # le scénario appairé ; None = matière hors référentiel (ADR-027).
    ref_id = get_referentiel_id_for_sequence(sid)
    context = {
        "sequence": sequence,
        "base_url": f"/sequence/editeur/{sid}",
        "steps": steps(sequence),
        # Niveaux CONTRAINTS par le référentiel (ADR-023) : une séquence 2TNE ne
        # propose que les FormationNiveau de sa formation ; hors référentiel,
        # liste générique.
        "niveau_classe_id_choices": (
            get_niveau_choices_pour_referentiel(int(ref_id))
            if ref_id is not None else get_niveau_classe_choices()
        ),
        "referentiel_actuel": get_referentiel(int(ref_id)) if ref_id is not None else None,
        "organisation_actuelle": mode_organisation(sequence),
        "seances": seances,
        # Valeurs DÉRIVÉES des séances (étape Cadre, lecture seule) : durée
        # cumulée et prérequis agrégés.
        "duree_cumulee": duree_lisible(duree_cumulee_minutes(sid)),
        "prerequis_derives": prerequis_par_seance(sid),
        # Scénario appairé (ADR-029) : navigation standard du tunnel vers lui.
        "scenario_lie": (
            get_scenario(int(scenario_id))
            if (scenario_id := get_scenario_id_for_sequence(sid)) is not None
            else None
        ),
    }
    context.update(navigation(etape))
    # Contexte de l'étape Connaissances (arbre, liens, compétence active…).
    context.update(contexte_connaissances(sid))
    return context


class SequenceEditeurController(BaseController):

    @staticmethod
    def nouveau(request: Request) -> Response:
        """Création inline (séquence-first, ADR-029) : crée la paire séquence +
        scénario jumeau, puis ouvre l'éditeur tunnel. Le titre est obligatoire ;
        le référentiel est facultatif (posé sur le scénario jumeau) ; l'identifiant
        est dérivé du titre et le niveau se renseigne ensuite."""
        titre = (request.form("titre", "") or "").strip()
        referentiel_id = parse_id(request.form("referentiel_id", ""))
        # Choix explicite rattachée / hors référentiel : « hors » ignore le
        # sélecteur (qui reste soumis, simplement masqué par le CSS).
        if request.form("mode_referentiel", "") == "hors":
            referentiel_id = None
        refs_valides = {int(r["Id"]) for r in list_referentiels()}
        if referentiel_id is not None and referentiel_id not in refs_valides:
            referentiel_id = None
        if not titre:
            return BaseController.redirect(
                "/sequence", request=request,
                flash="Le titre est obligatoire.", level="success",
            )
        # Le scénario jumeau porte le même titre, et le titre du scénario est unique.
        if titre_existe(titre):
            return BaseController.redirect(
                "/sequence", request=request,
                flash=f"Une séquence porte déjà le titre « {titre} ». Choisissez un titre différent !",
                level="success",
            )
        sid = creer_sequence_et_scenario(titre, referentiel_id)
        return BaseController.redirect(f"/sequence/editeur/{sid}")

    @staticmethod
    def editeur(request: Request) -> Response:
        sid = parse_id(request.route("id"))
        if sid is None:
            return BaseController.not_found()
        # Statut DÉRIVÉ mais persisté : auto-réparation à l'ouverture, sinon il
        # reste figé sur une règle périmée quand le cycle évolue (ADR-037).
        recalculer_statut(sid)
        sequence = get_sequence_by_id(sid)
        if sequence is None:
            return BaseController.not_found()
        etape = borner_etape(request.query("etape", "titre"))
        context = _contexte_editeur(sequence, etape)
        template = "app/sequence_editeur/_corps.html" if est_htmx(request) else "app/sequence_editeur/editeur.html"
        return BaseController.render(template, context=context, request=request)

    @staticmethod
    def enregistrer_identite(request: Request) -> Response:
        sid = parse_id(request.route("id"))
        if sid is None:
            return BaseController.not_found()
        sequence = get_sequence_by_id(sid)
        if sequence is None:
            return BaseController.not_found()
        # Niveau obligatoire (nullable en base pour l'état pré-saisie) : une
        # soumission vide ne doit jamais effacer un niveau déjà choisi.
        niveau = parse_id(request.form("niveau_classe_id", ""))
        # Encadré « Activité » : choix radio exclusif, projeté sur les deux
        # booléens du contrat. Valeur inconnue -> on conserve le mode en place.
        organisation = (request.form("organisation", "") or "").strip()
        if organisation not in ORGANISATIONS:
            # Peut rester None : « à préciser » tant qu'aucun mode n'est coché
            # (le choix est conscient, complément ADR-034).
            organisation = mode_organisation(sequence)
        # Nature (ADR-036) : formative par défaut ; valeur inconnue -> on
        # conserve la nature en place.
        nature = (request.form("nature", "") or "").strip()
        if nature not in NATURES:
            nature = str(sequence.get("Nature") or "formative")
        # Titre : jamais vide, toujours UNIQUE (garde au renommage). En cas de
        # refus, le titre en place est conservé et un toast d'erreur l'explique.
        titre_saisi = (request.form("titre", "") or "").strip()
        erreur = None
        if not titre_saisi:
            erreur = "Le titre ne peut pas être vide : titre non modifié."
            titre_saisi = str(sequence.get("Titre") or "")
        elif titre_saisi != sequence.get("Titre") and titre_sequence_existe_autre(titre_saisi, sid):
            erreur = f"Une séquence s'intitule déjà « {titre_saisi} » : titre non modifié."
            titre_saisi = str(sequence.get("Titre") or "")
        data = {
            "titre": titre_saisi,
            "activite_glissante": (1 if organisation == "glissante" else 0) if organisation else None,
            "ordre_impose": (1 if organisation == "ordre_impose" else 0) if organisation else None,
            "nature": nature,
            "niveau_classe_id": niveau if niveau is not None else sequence.get("niveau_classe_id"),
        }
        update_identite(sid, data)
        # Titre/niveau conditionnent la complétude : le statut peut basculer
        # (brouillon <-> finalise, dépublication si incomplète) — ADR-034.
        recalculer_statut(sid)
        return SequenceEditeurController._retour_sauvegarde(request, sid, "titre", erreur=erreur)

    @staticmethod
    def enregistrer_cadre(request: Request) -> Response:
        sid = parse_id(request.route("id"))
        if sid is None:
            return BaseController.not_found()
        if get_sequence_by_id(sid) is None:
            return BaseController.not_found()
        # Ni duree_estimee ni prerequis : ces valeurs sont dérivées des séances
        # rattachées (affichées en lecture seule dans l'étape).
        data = {
            "positionnement_progression": (request.form("positionnement_progression", "") or "").strip() or None,
            "modalites_evaluation": (request.form("modalites_evaluation", "") or "").strip() or None,
        }
        update_cadre(sid, data)
        return SequenceEditeurController._retour_sauvegarde(request, sid, "cadre")

    @staticmethod
    def _retour_sauvegarde(request: Request, sid: int, etape: str, erreur=None) -> Response:
        """Toast hors-bande en HTMX (avec stepper recalculé) ; redirection sans JS.

        Le stepper est renvoyé hors-bande pour que la complétion des étapes
        suive la saisie sans attendre une navigation (retour porteur).
        """
        if est_htmx(request):
            sequence = get_sequence_by_id(sid)
            context = {}
            if sequence is not None:
                scenario_id = get_scenario_id_for_sequence(sid)
                context = {
                    "steps": steps(sequence),
                    "etape": etape,
                    "base_url": f"/sequence/editeur/{sid}",
                    # Arbre « Famille pédagogique » hors-bande (nature/titre à jour).
                    "arbre_oob": True,
                    "sequence": sequence,
                    "scenario_lie": get_scenario(int(scenario_id)) if scenario_id is not None else None,
                    "seances": feuilles_famille(sid, sequence.get("Nature")),
                    "referentiel_actuel": (
                        get_referentiel(int(rid))
                        if (rid := get_referentiel_id_for_sequence(sid)) is not None
                        else None
                    ),
                    "message_erreur": erreur,
                }
            return BaseController.render(
                "app/sequence_editeur/_sauvegarde_oob.html", context=context, request=request
            )
        return BaseController.redirect(f"/sequence/editeur/{sid}", request=request)
