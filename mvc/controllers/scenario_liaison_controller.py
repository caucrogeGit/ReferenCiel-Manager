# pyright: strict
"""Liaison au référentiel dans l'éditeur de scénario (ADR-019, ADR-021, ADR-022).

Cochage unitaire des activités et critères (maître-détail HTMX) et gestion des
indicateurs de réussite d'un critère. Extrait de `ScenarioEditeurController`
pour garder chaque contrôleur sur une responsabilité ; les routes restent sous
`/conception/scenario` (mêmes chemins, mêmes noms, même garde RBAC).
"""
from typing import Any, cast

from core.http.request import Request
from core.http.response import Response
from core.mvc.controller.base_controller import BaseController

from mvc.helpers.htmx import est_htmx
from mvc.models.referentiel_atelier_model import (
    ajouter_indicateur as _ajouter_indicateur,
    competences_valides,
    get_arbre,
    get_critere,
    supprimer_indicateur as _supprimer_indicateur,
)
from mvc.models.scenario_editeur_model import (
    delier_activite,
    delier_critere,
    elaguer_criteres_hors_activites,
    get_activite_ids,
    get_critere_ids,
    get_scenario,
    lier_activite,
    lier_critere,
    recalculer_statut,
)
from mvc.services.scenario_tunnel import parse_id, selection_courante


class ScenarioLiaisonController(BaseController):

    # ── Cochage unitaire (activité / critère) ────────────────────────────────
    #
    # Le cochage ne passe plus par un gros POST « enregistrer la liaison » :
    # chaque case bascule seule, et on renvoie le maître-détail complet pour
    # que le compteur de la colonne de gauche suive. `enregistrer_liaison`
    # (POST global) reste en place pour le mode sans JS.

    @staticmethod
    def _basculer(request: Request, champ: str, fragment: str) -> Response:
        scenario_id = parse_id(request.route("id"))
        if scenario_id is None or get_scenario(scenario_id) is None:
            return BaseController.not_found()

        cible_id = parse_id(request.form(champ))
        if cible_id is None:
            return BaseController.not_found()

        # Écriture CIBLÉE du seul lien basculé (pas de réécriture de la liste
        # entière) : deux cases basculées « en même temps » émettent des requêtes
        # HTMX concurrentes ; en touchant des lignes distinctes, elles ne
        # s'écrasent plus (un décochage ne peut plus être « ressuscité » par la
        # relecture d'une autre requête).
        if champ == "activite":
            if cible_id in get_activite_ids(scenario_id):
                delier_activite(scenario_id, cible_id)
            else:
                lier_activite(scenario_id, cible_id)
            # Le jeu d'activités a changé : purge les critères des compétences qui
            # ne sont plus mobilisées (elles deviennent grisées « non valide »).
            elaguer_criteres_hors_activites(scenario_id)
        else:
            if cible_id in get_critere_ids(scenario_id):
                delier_critere(scenario_id, cible_id)
            else:
                lier_critere(scenario_id, cible_id)
        recalculer_statut(scenario_id)

        # Relecture après écriture, pour le rendu (compteur) et la redirection.
        activite_ids = get_activite_ids(scenario_id)
        critere_ids = get_critere_ids(scenario_id)

        # Sans JS : on retombe sur la page, à la bonne étape et au bon endroit.
        if not est_htmx(request):
            pole = request.form("pole", "")
            comp = request.form("competence", "")
            suffixe = f"&pole={pole}" if pole else ""
            suffixe += f"&competence={comp}" if comp else ""
            return BaseController.redirect(
                f"/conception/scenario/{scenario_id}?etape=liaison{suffixe}",
                request=request,
            )

        # Avec JS : on renvoie le bloc maître-détail concerné (compteur inclus).
        scenario = cast("dict[str, Any]", get_scenario(scenario_id))
        referentiel_id = scenario.get("referentiel_id")
        arbre = get_arbre(int(referentiel_id)) if referentiel_id else None
        pole_id, competence_id = selection_courante(
            arbre,
            request.query("pole") or request.form("pole", ""),
            request.query("competence") or request.form("competence", ""),
        )
        context: dict[str, Any] = {
            "scenario": scenario,
            "arbre": arbre,
            "activite_ids": activite_ids,
            "critere_ids": critere_ids,
            "pole_id": pole_id,
            "competence_id": competence_id,
            "base_url": f"/conception/scenario/{scenario_id}",
            "competences_valides": (
                competences_valides(int(referentiel_id), activite_ids)
                if referentiel_id else set()
            ),
        }
        # Basculer une ACTIVITÉ change la validité des compétences (relation n-n) :
        # on renvoie le bloc Pôles (cible du swap) ET le bloc Compétences rafraîchi
        # hors-bande (hx-swap-oob). Basculer un critère ne touche que les critères.
        template = (
            "app/scenario_editeur/_basculer_activite.html"
            if fragment == "poles"
            else "app/scenario_editeur/_bloc_competences.html"
        )
        return BaseController.render(template, context=context, request=request)

    @staticmethod
    def basculer_activite(request: Request) -> Response:
        return ScenarioLiaisonController._basculer(request, "activite", "poles")

    @staticmethod
    def basculer_critere(request: Request) -> Response:
        return ScenarioLiaisonController._basculer(request, "critere", "competences")

    # ── Indicateurs de réussite d'un critère (définis par le professeur) ──────
    #
    # Les indicateurs sont RÉFÉRENTIEL-level (partagés par tous les scénarios qui
    # utilisent ce critère). L'édition depuis le tunnel écrit donc sur le critère
    # du référentiel. On renvoie le fragment _detail_competence pour rafraîchir.

    @staticmethod
    def _rendre_detail_competence(request: Request, scenario_id: int) -> Response:
        comp = request.form("competence", "")
        # Sans JS : retour à la page, étape liaison, sur la bonne compétence.
        if not est_htmx(request):
            suffixe = f"&competence={comp}" if comp else ""
            return BaseController.redirect(
                f"/conception/scenario/{scenario_id}?etape=liaison{suffixe}",
                request=request,
            )
        scenario = cast("dict[str, Any]", get_scenario(scenario_id))
        referentiel_id = scenario.get("referentiel_id")
        arbre = get_arbre(int(referentiel_id)) if referentiel_id else None
        competence_id = parse_id(comp)
        if competence_id is None and arbre:
            comps: list[dict[str, Any]] = arbre.get("competences") or []
            competence_id = int(comps[0]["Id"]) if comps else None
        return BaseController.render(
            "app/scenario_editeur/_detail_competence.html",
            context={
                "arbre": arbre,
                "competence_id": competence_id,
                "critere_ids": get_critere_ids(scenario_id),
                "base_url": f"/conception/scenario/{scenario_id}",
            },
            request=request,
        )

    @staticmethod
    def ajouter_indicateur(request: Request) -> Response:
        scenario_id = parse_id(request.route("id"))
        critere_id = parse_id(request.route("cid"))
        if scenario_id is None or get_scenario(scenario_id) is None or critere_id is None:
            return BaseController.not_found()
        if get_critere(critere_id) is None:
            return BaseController.not_found()
        libelle = request.form("libelle", "").strip()
        if libelle:
            _ajouter_indicateur(critere_id, libelle)
        return ScenarioLiaisonController._rendre_detail_competence(request, scenario_id)

    @staticmethod
    def supprimer_indicateur(request: Request) -> Response:
        scenario_id = parse_id(request.route("id"))
        indicateur_id = parse_id(request.route("iid"))
        if scenario_id is None or get_scenario(scenario_id) is None or indicateur_id is None:
            return BaseController.not_found()
        _supprimer_indicateur(indicateur_id)
        return ScenarioLiaisonController._rendre_detail_competence(request, scenario_id)
