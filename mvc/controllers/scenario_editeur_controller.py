# pyright: strict
"""Éditeur de scénario (ADR-019) : conception sur mesure, alignée cpro-education.

Interface principale de conception d'un scénario, en 4 sections (Titre, Contexte,
Liaison avec le référentiel, Ressources), remplaçant le CRUD plat. La logique
pure du tunnel (étapes, complétion dérivée, sélection) vit dans
`mvc.services.scenario_tunnel` ; le cochage unitaire et les indicateurs dans
`ScenarioLiaisonController`. La Liaison consomme l'arbre de l'atelier
référentiel (ADR-018).
"""
import html
from typing import Any

from core.http.request import Request
from core.http.response import Response
from core.mvc.controller.base_controller import BaseController
from core.auth.session import get_authenticated_user_id
from core.security.session import get_flash, get_session_id

from forge_mvc_files import UploadError, delete_upload, save_upload

from mvc.helpers.htmx import est_htmx
from mvc.models.referentiel_atelier_model import (
    competences_valides,
    get_arbre,
    list_referentiels,
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
from mvc.services.scenario_pdf import construire_pdf
from mvc.services.scenario_tunnel import (
    borner_etape,
    navigation,
    ouvrir_sur_selection,
    parse_id,
    parse_ids,
    selection_courante,
    slug,
    steps,
)


class ScenarioEditeurController(BaseController):

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
        referentiel_id = parse_id(request.form("referentiel_id", ""))
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

    # ── Vue principale ───────────────────────────────────────────────────────

    @staticmethod
    def editeur(request: Request) -> Response:
        scenario_id = parse_id(request.route("id"))
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

        etape = borner_etape(request.query("etape", "titre"))
        pole_id, competence_id = selection_courante(
            arbre,
            request.query("pole") or request.form("pole", ""),
            request.query("competence") or request.form("competence", ""),
        )
        # À l'arrivée (pas de choix explicite), ouvrir le 1er item déjà coché pour
        # rendre les sélections visibles derrière les badges de comptage.
        pole_id, competence_id = ouvrir_sur_selection(
            arbre, pole_id, competence_id, activite_ids, critere_ids
        )
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
            # état du tunnel (etape, position, total, prev, next)
            **navigation(etape),
            "steps": steps(scenario, activite_ids, critere_ids),
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
        if est_htmx(request):
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

    # ── Sections du tunnel (enregistrements) ─────────────────────────────────

    @staticmethod
    def enregistrer_titre(request: Request) -> Response:
        scenario_id = parse_id(request.route("id"))
        if scenario_id is None:
            return BaseController.not_found()
        if get_scenario(scenario_id) is None:
            return BaseController.not_found()
        htmx = est_htmx(request)
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
            [i for i in parse_ids(request.body.get("co_auteurs", [])) if i in pool]
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
        # Auto-enregistrement HTMX : le toast « Enregistré » est hors-bande, et son
        # contenu restant (vide) efface la zone d'erreur #titre-erreur (cible du
        # formulaire) — donc un message d'unicité précédent disparaît. Sans JS, le
        # <noscript> soumet le formulaire (redirection ci-dessous).
        if htmx:
            return BaseController.render(
                "app/scenario_editeur/_sauvegarde_oob.html", context={}, request=request
            )
        return BaseController.redirect(
            f"/conception/scenario/{scenario_id}", request=request, flash="Section Titre enregistrée."
        )

    @staticmethod
    def enregistrer_contexte(request: Request) -> Response:
        scenario_id = parse_id(request.route("id"))
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
        # Auto-enregistrement HTMX (à la saisie) : le contexte complet peut faire
        # basculer le statut en « finalisé ». Le formulaire est en hx-swap="none",
        # donc on renvoie UNIQUEMENT le badge hors-bande (hx-swap-oob) : l'en-tête
        # se met à jour, rien d'autre n'est touché. Sans JS, le <noscript> soumet
        # le formulaire et on retombe sur la redirection ci-dessous.
        if est_htmx(request):
            return BaseController.render(
                "app/scenario_editeur/_feedback_ecriture.html",
                context={"scenario": get_scenario(scenario_id)},
                request=request,
            )
        return BaseController.redirect(
            f"/conception/scenario/{scenario_id}", request=request, flash="Section Contexte enregistrée."
        )

    @staticmethod
    def enregistrer_referentiel(request: Request) -> Response:
        scenario_id = parse_id(request.route("id"))
        if scenario_id is None or get_scenario(scenario_id) is None:
            return BaseController.not_found()
        referentiel_id = parse_id(request.form("referentiel_id", ""))
        if referentiel_id is not None:
            enregistrer_referentiel(scenario_id, referentiel_id)
        return BaseController.redirect(
            f"/conception/scenario/{scenario_id}", request=request, flash="Référentiel rattaché."
        )

    @staticmethod
    def enregistrer_liaison(request: Request) -> Response:
        scenario_id = parse_id(request.route("id"))
        if scenario_id is None or get_scenario(scenario_id) is None:
            return BaseController.not_found()
        activite_ids = parse_ids(request.body.get("activites", []))
        critere_ids = parse_ids(request.body.get("criteres", []))
        enregistrer_liaison(scenario_id, activite_ids, critere_ids)
        recalculer_statut(scenario_id)
        return BaseController.redirect(
            f"/conception/scenario/{scenario_id}", request=request, flash="Liaison au référentiel enregistrée."
        )

    # ── Ressources ───────────────────────────────────────────────────────────

    @staticmethod
    def uploader_ressource(request: Request) -> Response:
        scenario_id = parse_id(request.route("id"))
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
        scenario_id = parse_id(request.route("id"))
        ressource_id = parse_id(request.route("rid"))
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

    # ── Export PDF (ADR-024) ─────────────────────────────────────────────────

    @staticmethod
    def telecharger_pdf(request: Request) -> Response:
        scenario_id = parse_id(request.route("id"))
        if scenario_id is None:
            return BaseController.not_found()
        scenario = get_scenario(scenario_id)
        if scenario is None:
            return BaseController.not_found()
        # Réservé aux scénarios finalisés (ou déjà utilisés : contenu complet, figé).
        if scenario.get("Statut") not in ("finalise", "utilise"):
            return BaseController.redirect_with_flash(
                request,
                f"/conception/scenario/{scenario_id}?etape=titre",
                "Le PDF n'est disponible que pour un scénario finalisé.",
                "error",
            )
        pdf = construire_pdf(scenario_id)
        nom = slug(str(scenario.get("Titre") or "scenario"))
        return Response(
            200,
            pdf,
            "application/pdf",
            headers={"Content-Disposition": f'attachment; filename="scenario-{nom}.pdf"'},
        )
