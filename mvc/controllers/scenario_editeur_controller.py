# pyright: strict
"""Éditeur de scénario (ADR-019) : conception sur mesure, alignée cpro-education.

Interface principale de conception d'un scénario, en 4 sections (Titre, Contexte,
Liaison avec le référentiel, Ressources), remplaçant le CRUD plat. Phase 1 : la
section Titre (titre, co-intervention, co-auteurs). La Liaison consommera l'arbre
de l'atelier référentiel (ADR-018).
"""
import html
from typing import Any, cast

from core.http.request import Request
from core.http.response import Response
from core.mvc.controller.base_controller import BaseController
from core.auth.session import get_authenticated_user_id
from core.security.session import get_flash, get_session_id

from forge_mvc_files import UploadError, delete_upload, save_upload

from mvc.models.referentiel_atelier_model import (
    ajouter_indicateur as _ajouter_indicateur,
    competences_valides,
    get_arbre,
    get_critere,
    list_referentiels,
    supprimer_indicateur as _supprimer_indicateur,
)
from mvc.models.scenario_editeur_model import (
    ajouter_ressource,
    creer_scenario,
    titre_existe,
    titre_existe_autre,
    enregistrer_contexte,
    enregistrer_liaison,
    enregistrer_referentiel,
    enregistrer_titre,
    lier_activite,
    delier_activite,
    lier_critere,
    delier_critere,
    elaguer_criteres_hors_activites,
    get_activite_ids,
    get_co_auteur_ids,
    get_critere_ids,
    get_ressource,
    get_scenario,
    list_professeurs,
    recalculer_statut,
    list_ressources,
    list_scenarios,
    supprimer_ressource,
)


# État du tunnel (ADR-021) : les 4 étapes et leurs libellés. La complétion n'est
# jamais persistée, elle est dérivée des données (voir _steps).
ETAPES: tuple[str, ...] = ("titre", "contexte", "liaison", "ressources")

_LIBELLES: dict[str, str] = {
    "titre": "Titre",
    "contexte": "Contexte",
    "liaison": "Liaison référentiel",
    "ressources": "Ressources",
}


class ScenarioEditeurController(BaseController):

    @staticmethod
    def _parse_id(raw: object) -> "int | None":
        try:
            return int(raw)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _parse_many_ids(request: Request, field_name: str) -> list[int]:
        raw: Any = request.body.get(field_name, [])
        if isinstance(raw, list):
            values: list[Any] = cast("list[Any]", raw)
        elif raw:
            values = [raw]
        else:
            values = []
        out: list[int] = []
        for value in values:
            try:
                n = int(value)
            except (TypeError, ValueError):
                continue
            if n > 0 and n not in out:
                out.append(n)
        return out

    @staticmethod
    def index(request: Request) -> Response:
        return BaseController.render(
            "app/scenario_editeur/index.html",
            context={
                "scenarios": list_scenarios(),
                "referentiels": list_referentiels(),
                "flash": get_flash(get_session_id(request)),
            },
            request=request,
        )

    @staticmethod
    def nouveau(request: Request) -> Response:
        # Le référentiel est obligatoire dès la création (ADR-023) : formation,
        # niveau et débouchés s'en déduisent. On vérifie côté serveur qu'il existe.
        titre = request.form("titre", "").strip()
        referentiel_id = ScenarioEditeurController._parse_id(request.form("referentiel_id", ""))
        refs_valides = {int(r["Id"]) for r in list_referentiels()}
        if not titre or referentiel_id is None or referentiel_id not in refs_valides:
            return BaseController.redirect(
                "/conception/scenario",
                request=request,
                flash="Titre et référentiel sont obligatoires pour créer un scénario.",
                level="success",
            )
        # Le titre d'un scénario est unique.
        if titre_existe(titre):
            return BaseController.redirect(
                "/conception/scenario",
                request=request,
                flash=f"Un scénario s'intitule déjà « {titre} ». Choisissez un autre titre !",
                level="success",
            )
        scenario_id = creer_scenario(titre, referentiel_id)
        return BaseController.redirect(f"/conception/scenario/{scenario_id}")

    # ── Helpers d'état du tunnel (ADR-021) ───────────────────────────────────

    @staticmethod
    def _is_htmx(request: Request) -> bool:
        return request.header("HX-Request") is not None

    @staticmethod
    def _etape(request: Request) -> str:
        """Étape demandée, bornée à la liste connue (défaut : titre)."""
        raw = request.query("etape", "titre")
        return raw if raw in ETAPES else "titre"

    @staticmethod
    def _steps(
        scenario: dict[str, Any],
        arbre: "dict[str, Any] | None",
        referentiels: list[dict[str, Any]],
        activite_ids: list[int],
        critere_ids: list[int],
        ressources: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Barre d'étapes : la complétion est DÉRIVÉE des données.

        Rien n'est persisté pour l'UI ; l'indicateur de chaque étape est aligné sur
        la règle de statut (recalculer_statut) : « finalisé » = contexte complet ET
        au moins une activité ET au moins un critère.
        """
        #  - Titre : rempli dès la création (obligatoire).
        #  - Contexte : les 5 champs cpro sont tous obligatoires (d'où all()).
        #  - Liaison : au moins une activité ET un critère (contribue à « finalisé »).
        #  - Ressources : facultatives -> l'étape ne bloque jamais.
        contexte_complet = all(
            scenario.get(champ)
            for champ in (
                "DescriptionContexte",
                "Problematique",
                "MaterielsLogiciels",
                "LiensAssocies",
                "EspacesFormation",
            )
        )
        liaison_complete = len(activite_ids) > 0 and len(critere_ids) > 0

        return [
            {
                "key": "titre",
                "label": _LIBELLES["titre"],
                "badge": "",
                "done": bool(scenario.get("Titre")),
            },
            {
                "key": "contexte",
                "label": _LIBELLES["contexte"],
                "badge": "",
                "done": contexte_complet,
            },
            {
                "key": "liaison",
                "label": _LIBELLES["liaison"],
                # Le code du référentiel (ex. « ciel-2tne ») est rappelé sous le titre.
                "badge": "",
                "done": liaison_complete,
            },
            {
                "key": "ressources",
                "label": _LIBELLES["ressources"],
                "badge": "",
                "done": True,
            },
        ]

    @staticmethod
    def _selection_courante(
        request: Request, arbre: "dict[str, Any] | None"
    ) -> "tuple[int | None, int | None]":
        """Pôle et compétence actifs, ou None si aucun n'est encore choisi.

        À l'arrivée sur l'étape (aucun `pole`/`competence` dans la requête), on ne
        présélectionne rien : chaque colonne de détail invite explicitement à
        choisir un item. L'item actif est porté par l'URL (lien maître, hx-get) ou
        par le formulaire de cochage (hx-post) — jamais deviné par défaut.
        """
        if not arbre:
            return None, None
        pole_id = ScenarioEditeurController._parse_id(
            request.query("pole") or request.form("pole", "")
        )
        comp_id = ScenarioEditeurController._parse_id(
            request.query("competence") or request.form("competence", "")
        )
        return pole_id, comp_id

    @staticmethod
    def _ouvrir_sur_selection(
        arbre: "dict[str, Any] | None",
        pole_id: "int | None",
        competence_id: "int | None",
        activite_ids: list[int],
        critere_ids: list[int],
    ) -> "tuple[int | None, int | None]":
        """À l'arrivée sur l'étape (aucun item explicitement demandé), ouvre le
        premier pôle et la première compétence QUI ONT des cases cochées, pour
        montrer d'emblée les sélections du scénario (sinon l'utilisateur voit un
        badge de comptage sans pouvoir le rapprocher d'un détail). Un scénario
        vierge reste sans rien d'ouvert. N'écrase jamais un choix explicite."""
        if not arbre:
            return pole_id, competence_id
        if pole_id is None:
            pole_id = next(
                (int(p["Id"]) for p in arbre.get("poles", [])
                 if any(int(a["Id"]) in activite_ids for a in p.get("activites", []))),
                None,
            )
        if competence_id is None:
            competence_id = next(
                (int(c["Id"]) for c in arbre.get("competences", [])
                 if any(int(cr["Id"]) in critere_ids for cr in c.get("criteres", []))),
                None,
            )
        return pole_id, competence_id

    # ── Vue principale ───────────────────────────────────────────────────────

    @staticmethod
    def editeur(request: Request) -> Response:
        scenario_id = ScenarioEditeurController._parse_id(request.route("id"))
        if scenario_id is None:
            return BaseController.not_found()
        scenario = get_scenario(scenario_id)
        if scenario is None:
            return BaseController.not_found()

        referentiel_id = scenario.get("referentiel_id")
        arbre = get_arbre(int(referentiel_id)) if referentiel_id else None
        referentiels = list_referentiels()
        activite_ids = get_activite_ids(scenario_id)
        critere_ids = get_critere_ids(scenario_id)
        ressources = list_ressources(scenario_id)
        co_auteur_ids = get_co_auteur_ids(scenario_id)

        etape = ScenarioEditeurController._etape(request)
        pole_id, competence_id = ScenarioEditeurController._selection_courante(
            request, arbre
        )
        # À l'arrivée (pas de choix explicite), ouvrir le 1er item déjà coché pour
        # rendre les sélections visibles derrière les badges de comptage.
        pole_id, competence_id = ScenarioEditeurController._ouvrir_sur_selection(
            arbre, pole_id, competence_id, activite_ids, critere_ids
        )
        steps = ScenarioEditeurController._steps(
            scenario, arbre, referentiels, activite_ids, critere_ids, ressources
        )
        position = ETAPES.index(etape) + 1
        # Référentiel courant (rappelé sous le titre) et gate d'enregistrement :
        # le scénario n'est enregistrable que si les 4 étapes sont saisies (ADR-019).
        referentiel = next(
            (r for r in referentiels if r["Id"] == referentiel_id), None
        )

        context: dict[str, Any] = {
            "scenario": scenario,
            "flash": get_flash(get_session_id(request)),
            "co_auteur_ids": co_auteur_ids,
            # Co-auteurs possibles : tous les professeurs SAUF le compte courant
            # (l'auteur ne peut pas être son propre co-enseignant).
            "professeurs": list_professeurs(exclure_user_id=get_authenticated_user_id(request)),
            "referentiels": referentiels,
            "referentiel": referentiel,
            "arbre": arbre,
            "activite_ids": activite_ids,
            "critere_ids": critere_ids,
            "ressources": ressources,
            # état du tunnel
            "etape": etape,
            "steps": steps,
            "position": position,
            "total": len(ETAPES),
            "prev": (
                {"key": ETAPES[position - 2], "label": _LIBELLES[ETAPES[position - 2]]}
                if position > 1
                else None
            ),
            "next": (
                {"key": ETAPES[position], "label": _LIBELLES[ETAPES[position]]}
                if position < len(ETAPES)
                else None
            ),
            "base_url": f"/conception/scenario/{scenario_id}",
            "pole_id": pole_id,
            "competence_id": competence_id,
            # Compétences évaluables = celles mobilisées par les activités cochées
            # (relation n-n). Les autres sont grisées « non valide » dans le bloc.
            "competences_valides": (
                competences_valides(int(referentiel_id), activite_ids)
                if referentiel_id else set()
            ),
        }

        # Fragment HTMX : on ne renvoie que le partial, sans le layout. Rendu
        # Jinja NORMAL (pas raw=True : dans Forge, raw sert un fichier brut, sans
        # rendu ni contexte). Un partial ne fait pas {% extends base %}, donc le
        # rendu normal produit le fragment seul, avec csrf_token/can() injectés.
        if ScenarioEditeurController._is_htmx(request):
            cible = request.query("fragment", "")
            # Navigation dans un maître-détail : on renvoie le BLOC entier
            # (colonne maître + détail) pour que la surbrillance de l'item actif
            # suive le clic. Swap outerHTML sur #bloc-poles / #bloc-competences.
            if cible == "pole":
                return BaseController.render(
                    "app/scenario_editeur/_bloc_poles.html",
                    context=context,
                    request=request,
                )
            if cible == "competence":
                return BaseController.render(
                    "app/scenario_editeur/_bloc_competences.html",
                    context=context,
                    request=request,
                )
            # Navigation d'étape : on renvoie le corps entier (stepper + étape)
            # pour que le stepper reflète l'étape sélectionnée (#tunnel-corps).
            return BaseController.render(
                "app/scenario_editeur/_corps.html",
                context=context,
                request=request,
            )

        return BaseController.render(
            "app/scenario_editeur/editeur.html",
            context=context,
            request=request,
        )

    @staticmethod
    def enregistrer_titre(request: Request) -> Response:
        scenario_id = ScenarioEditeurController._parse_id(request.route("id"))
        if scenario_id is None:
            return BaseController.not_found()
        if get_scenario(scenario_id) is None:
            return BaseController.not_found()
        htmx = ScenarioEditeurController._is_htmx(request)
        titre = request.form("titre", "").strip()
        co_intervention = request.form("co_intervention", "") != ""
        # Pool des co-auteurs possibles : tous les professeurs SAUF le compte courant.
        pool = {
            int(p["Id"])
            for p in list_professeurs(exclure_user_id=get_authenticated_user_id(request))
        }
        # Ceinture-bretelles : en co-intervention, on ne persiste que des co-auteurs
        # DU pool (donc jamais le prof courant, même si le formulaire était forgé).
        co_auteur_ids = (
            [i for i in ScenarioEditeurController._parse_many_ids(request, "co_auteurs") if i in pool]
            if co_intervention
            else []
        )
        # Titre unique (contrainte en base) : on refuse un renommage qui collerait
        # à un autre scénario, plutôt que de heurter la contrainte (500). La réponse
        # HTMX alimente la zone d'erreur #titre-erreur (message si collision, sinon vide).
        if titre and titre_existe_autre(titre, scenario_id):
            if htmx:
                return Response(
                    body=f"Un autre scénario s'intitule déjà « {html.escape(titre)} »."
                )
            return BaseController.redirect(
                f"/conception/scenario/{scenario_id}",
                request=request,
                flash=f"Un autre scénario s'intitule déjà « {titre} ».",
                level="success",
            )
        # Co-intervention demandée mais aucun co-auteur possible : l'option est
        # indisponible, on ne l'active pas et on prévient (flash, page rechargée).
        if co_intervention and not pool:
            enregistrer_titre(scenario_id, titre, False, [])
            msg = "L'option co-intervention est indisponible : aucun autre professeur enregistré."
            if htmx:
                BaseController.set_flash(request, msg, "success")
                return Response(headers={"HX-Refresh": "true"})
            return BaseController.redirect(
                f"/conception/scenario/{scenario_id}", request=request, flash=msg, level="success"
            )
        enregistrer_titre(scenario_id, titre, co_intervention, co_auteur_ids)
        # Auto-enregistrement HTMX : on renvoie une zone d'erreur vide (efface un
        # message précédent). Sans JS, le <noscript> soumet le formulaire (redirection).
        if htmx:
            return Response(body="")
        return BaseController.redirect(
            f"/conception/scenario/{scenario_id}", request=request, flash="Section Titre enregistrée."
        )

    @staticmethod
    def enregistrer_contexte(request: Request) -> Response:
        scenario_id = ScenarioEditeurController._parse_id(request.route("id"))
        if scenario_id is None:
            return BaseController.not_found()
        if get_scenario(scenario_id) is None:
            return BaseController.not_found()
        enregistrer_contexte(
            scenario_id,
            request.form("description_contexte", "").strip(),
            request.form("problematique", "").strip(),
            request.form("materiels_logiciels", "").strip(),
            request.form("liens_associes", "").strip(),
            request.form("espaces_formation", "").strip(),
        )
        recalculer_statut(scenario_id)
        # Auto-enregistrement HTMX (à la saisie) : 204, pas de rechargement. Sans JS,
        # le <noscript> soumet le formulaire et on retombe sur la redirection.
        if ScenarioEditeurController._is_htmx(request):
            return Response(status=204)
        return BaseController.redirect(
            f"/conception/scenario/{scenario_id}", request=request, flash="Section Contexte enregistrée."
        )

    @staticmethod
    def enregistrer_referentiel(request: Request) -> Response:
        scenario_id = ScenarioEditeurController._parse_id(request.route("id"))
        if scenario_id is None or get_scenario(scenario_id) is None:
            return BaseController.not_found()
        referentiel_id = ScenarioEditeurController._parse_id(request.form("referentiel_id", ""))
        if referentiel_id is not None:
            enregistrer_referentiel(scenario_id, referentiel_id)
        return BaseController.redirect(
            f"/conception/scenario/{scenario_id}", request=request, flash="Référentiel rattaché."
        )

    @staticmethod
    def enregistrer_liaison(request: Request) -> Response:
        scenario_id = ScenarioEditeurController._parse_id(request.route("id"))
        if scenario_id is None or get_scenario(scenario_id) is None:
            return BaseController.not_found()
        activite_ids = ScenarioEditeurController._parse_many_ids(request, "activites")
        critere_ids = ScenarioEditeurController._parse_many_ids(request, "criteres")
        enregistrer_liaison(scenario_id, activite_ids, critere_ids)
        recalculer_statut(scenario_id)
        return BaseController.redirect(
            f"/conception/scenario/{scenario_id}", request=request, flash="Liaison au référentiel enregistrée."
        )

    @staticmethod
    def uploader_ressource(request: Request) -> Response:
        scenario_id = ScenarioEditeurController._parse_id(request.route("id"))
        if scenario_id is None or get_scenario(scenario_id) is None:
            return BaseController.not_found()
        # Retour sur l'étape Ressources (sans ?etape, l'éditeur retombe sur Titre).
        cible = f"/conception/scenario/{scenario_id}?etape=ressources"
        uploaded = request.file("fichier")
        if uploaded is None or not uploaded.filename:
            return BaseController.redirect_with_flash(request, cible, "Aucun fichier sélectionné.", "error")
        try:
            saved = save_upload(uploaded, category="scenarios")
        except UploadError as exc:
            return BaseController.redirect_with_flash(request, cible, f"Dépôt refusé : {exc}", "error")
        ajouter_ressource(scenario_id, saved.original_name, saved.path, saved.mime_type, saved.size)
        return BaseController.redirect_with_flash(request, cible, "Ressource ajoutée.", "success")

    @staticmethod
    def supprimer_ressource(request: Request) -> Response:
        scenario_id = ScenarioEditeurController._parse_id(request.route("id"))
        ressource_id = ScenarioEditeurController._parse_id(request.route("rid"))
        if scenario_id is None or ressource_id is None:
            return BaseController.not_found()
        ressource = get_ressource(ressource_id, scenario_id)
        if ressource is None:
            return BaseController.not_found()
        delete_upload(ressource["CheminMedia"])
        supprimer_ressource(ressource_id)
        return BaseController.redirect_with_flash(
            request,
            f"/conception/scenario/{scenario_id}?etape=ressources",
            "Ressource supprimée.",
            "success",
        )

    # ── Cochage unitaire (activité / critère) ────────────────────────────────
    #
    # Le cochage ne passe plus par un gros POST « enregistrer la liaison » :
    # chaque case bascule seule, et on renvoie le maître-détail complet pour
    # que le compteur de la colonne de gauche suive. `enregistrer_liaison`
    # (POST global) reste en place pour le mode sans JS.

    @staticmethod
    def _basculer(request: Request, champ: str, fragment: str) -> Response:
        scenario_id = ScenarioEditeurController._parse_id(request.route("id"))
        if scenario_id is None or get_scenario(scenario_id) is None:
            return BaseController.not_found()

        cible_id = ScenarioEditeurController._parse_id(request.form(champ))
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
        if not ScenarioEditeurController._is_htmx(request):
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
        pole_id, competence_id = ScenarioEditeurController._selection_courante(
            request, arbre
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
        return ScenarioEditeurController._basculer(request, "activite", "poles")

    @staticmethod
    def basculer_critere(request: Request) -> Response:
        return ScenarioEditeurController._basculer(request, "critere", "competences")

    # ── Indicateurs de réussite d'un critère (définis par le professeur) ──────
    #
    # Les indicateurs sont RÉFÉRENTIEL-level (partagés par tous les scénarios qui
    # utilisent ce critère). L'édition depuis le tunnel écrit donc sur le critère
    # du référentiel. On renvoie le fragment _detail_competence pour rafraîchir.

    @staticmethod
    def _rendre_detail_competence(request: Request, scenario_id: int) -> Response:
        comp = request.form("competence", "")
        # Sans JS : retour à la page, étape liaison, sur la bonne compétence.
        if not ScenarioEditeurController._is_htmx(request):
            suffixe = f"&competence={comp}" if comp else ""
            return BaseController.redirect(
                f"/conception/scenario/{scenario_id}?etape=liaison{suffixe}",
                request=request,
            )
        scenario = cast("dict[str, Any]", get_scenario(scenario_id))
        referentiel_id = scenario.get("referentiel_id")
        arbre = get_arbre(int(referentiel_id)) if referentiel_id else None
        competence_id = ScenarioEditeurController._parse_id(comp)
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
        scenario_id = ScenarioEditeurController._parse_id(request.route("id"))
        critere_id = ScenarioEditeurController._parse_id(request.route("cid"))
        if scenario_id is None or get_scenario(scenario_id) is None or critere_id is None:
            return BaseController.not_found()
        if get_critere(critere_id) is None:
            return BaseController.not_found()
        libelle = request.form("libelle", "").strip()
        if libelle:
            _ajouter_indicateur(critere_id, libelle)
        return ScenarioEditeurController._rendre_detail_competence(request, scenario_id)

    @staticmethod
    def supprimer_indicateur(request: Request) -> Response:
        scenario_id = ScenarioEditeurController._parse_id(request.route("id"))
        indicateur_id = ScenarioEditeurController._parse_id(request.route("iid"))
        if scenario_id is None or get_scenario(scenario_id) is None or indicateur_id is None:
            return BaseController.not_found()
        _supprimer_indicateur(indicateur_id)
        return ScenarioEditeurController._rendre_detail_competence(request, scenario_id)
