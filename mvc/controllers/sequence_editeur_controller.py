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
from mvc.services.sequence_tunnel import borner_etape, navigation, parse_id, steps
from mvc.models.sequence_model import (
    get_sequence_by_id,
    update_identite,
    update_cadre,
    get_niveau_classe_choices,
)
from mvc.models.scenario_editeur_model import creer_sequence_et_scenario, titre_existe
from mvc.models.seance_model import count_seances, find_seances_paginated
from mvc.models.sequence_connaissance_model import get_liens_by_sequence
from mvc.controllers.sequence_connaissance_controller import contexte_connaissances


def _contexte_editeur(sequence: dict, etape: str) -> dict:
    """Contexte complet de l'éditeur (coquille + étape active)."""
    sid = sequence["Id"]
    nb_connaissances = len(get_liens_by_sequence(sid))
    nb_seances = count_seances(filters={"sequence_id": sid})
    context = {
        "sequence": sequence,
        "base_url": f"/sequence/editeur/{sid}",
        "steps": steps(sequence, nb_connaissances, nb_seances),
        "niveau_classe_id_choices": get_niveau_classe_choices(),
        "seances": find_seances_paginated(filters={"sequence_id": sid}, limit=200),
    }
    context.update(navigation(etape))
    # Contexte de l'étape Connaissances (arbre, liens, compétence active…).
    context.update(contexte_connaissances(sid))
    return context


class SequenceEditeurController(BaseController):

    @staticmethod
    def nouveau(request: Request) -> Response:
        """Création inline (séquence-first, ADR-029) : crée la paire séquence +
        scénario jumeau, puis ouvre l'éditeur tunnel. Seul le titre est obligatoire ;
        l'identifiant est dérivé du titre, le niveau se renseigne ensuite."""
        titre = (request.form("titre", "") or "").strip()
        niveau = parse_id(request.form("niveau_classe_id", ""))
        niveaux_valides = {value for value, _ in get_niveau_classe_choices()}
        if niveau is not None and niveau not in niveaux_valides:
            niveau = None
        if not titre:
            return BaseController.redirect(
                "/sequence", request=request,
                flash="Le titre est obligatoire.", level="success",
            )
        # Le scénario jumeau porte le même titre, et le titre du scénario est unique.
        if titre_existe(titre):
            return BaseController.redirect(
                "/sequence", request=request,
                flash=f"Un scénario s'intitule déjà « {titre} ». Choisissez un autre titre !",
                level="success",
            )
        sid = creer_sequence_et_scenario(titre, niveau)
        return BaseController.redirect(f"/sequence/editeur/{sid}")

    @staticmethod
    def editeur(request: Request) -> Response:
        sid = parse_id(request.route("id"))
        if sid is None:
            return BaseController.not_found()
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
        data = {
            "titre": (request.form("titre", "") or "").strip(),
            "activite_glissante": 1 if request.form("activite_glissante", "") else 0,
            "ordre_impose": 1 if request.form("ordre_impose", "") else 0,
            # niveau_classe_id est nullable (ADR-029) : vide -> None.
            "niveau_classe_id": parse_id(request.form("niveau_classe_id", "")),
        }
        update_identite(sid, data)
        return SequenceEditeurController._retour_sauvegarde(request, sid)

    @staticmethod
    def enregistrer_cadre(request: Request) -> Response:
        sid = parse_id(request.route("id"))
        if sid is None:
            return BaseController.not_found()
        if get_sequence_by_id(sid) is None:
            return BaseController.not_found()
        data = {
            "prerequis": (request.form("prerequis", "") or "").strip() or None,
            "positionnement_progression": (request.form("positionnement_progression", "") or "").strip() or None,
            "duree_estimee": (request.form("duree_estimee", "") or "").strip() or None,
            "modalites_evaluation": (request.form("modalites_evaluation", "") or "").strip() or None,
        }
        update_cadre(sid, data)
        return SequenceEditeurController._retour_sauvegarde(request, sid)

    @staticmethod
    def _retour_sauvegarde(request: Request, sid: int) -> Response:
        """Toast hors-bande en HTMX ; redirection vers l'éditeur sans JS."""
        if est_htmx(request):
            return BaseController.render(
                "app/sequence_editeur/_sauvegarde_oob.html", context={}, request=request
            )
        return BaseController.redirect(f"/sequence/editeur/{sid}", request=request)
