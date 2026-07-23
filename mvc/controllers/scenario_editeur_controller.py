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
from collections.abc import Callable
from typing import Any, cast

from core.http.request import Request
from core.http.response import Response
from core.mvc.controller.base_controller import BaseController
from core.auth.session import get_authenticated_user_id
from core.security.session import get_flash, get_session_id

from forge_mvc_files import UploadError, delete_upload, save_upload

from mvc.helpers.htmx import est_htmx
from mvc.helpers.groupes import grouper, libelle_referentiel
from mvc.models.referentiel_atelier_model import (
    competences_valides,
    get_arbre,
    get_referentiel,
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
    get_sequence_appairee,
    list_scenarios,
    paire_est_finalisee,
    supprimer_ressource,
    supprimer_scenario,
)
from mvc.models.seance_model import feuilles_famille
from mvc.models.sequence_model import recalculer_statut as recalculer_statut_sequence
from mvc.services.scenario_pdf import construire_pdf
from mvc.services.scenario_export import construire_json, construire_markdown
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


def contexte_stepper(scenario: "dict[str, Any]", etape: str) -> "dict[str, Any]":
    """Stepper recalculé pour les réponses hors-bande : la complétion des
    sections suit chaque écriture, sur toutes les sections du tunnel."""
    scenario_id = int(scenario["Id"])
    return {
        "steps": steps(scenario, get_activite_ids(scenario_id), get_critere_ids(scenario_id)),
        "etape": etape,
        "base_url": f"/conception/scenario/{scenario_id}",
        "stepper_oob": True,
    }


def contexte_famille(scenario: "dict[str, Any]") -> "dict[str, Any]":
    """Contexte de l'arbre « Famille pédagogique » (en-tête des tunnels et
    rafraîchissement hors-bande) : paire, séances et référentiel."""
    scenario_id = int(scenario["Id"])
    ref_id = scenario.get("referentiel_id")
    sequence_liee = get_sequence_appairee(scenario_id)
    return {
        "scenario": scenario,
        "sequence_liee": sequence_liee,
        # Feuilles décorées d'un Finalise dérivé (coche de l'arbre, ADR-034/037).
        "seances_liees": (
            feuilles_famille(int(sequence_liee["Id"]), sequence_liee.get("Nature"))
            if sequence_liee is not None else []
        ),
        "referentiel_famille": get_referentiel(int(ref_id)) if ref_id else None,
    }


class ScenarioEditeurController(BaseController):

    @staticmethod
    def index(request: Request) -> Response:
        # Cartes classées par référentiel (sections), hors référentiel en fin.
        return BaseController.render(
            "app/scenario_editeur/index.html",
            context={
                "groupes": grouper(list_scenarios(), libelle_referentiel, "Hors référentiel"),
                "referentiels": list_referentiels(),
                "flash": get_flash(get_session_id(request)),
            },
            request=request,
        )

    @staticmethod
    def nouveau(request: Request) -> Response:
        # Titre obligatoire ; référentiel FACULTATIF (ADR-027 : matières non
        # adossées à un référentiel). S'il est fourni, il doit être valide ;
        # laissé vide = scénario hors référentiel (finalisable sur le seul contexte).
        titre = request.form("titre", "").strip()
        referentiel_id = parse_id(request.form("referentiel_id", ""))
        # Choix explicite rattaché / hors référentiel : « hors » ignore le
        # sélecteur (qui reste soumis, simplement masqué par le CSS).
        if request.form("mode_referentiel", "") == "hors":
            referentiel_id = None
        refs_valides = {int(r["Id"]) for r in list_referentiels()}
        if not titre or (referentiel_id is not None and referentiel_id not in refs_valides):
            return BaseController.redirect(
                "/conception/scenario",
                request=request,
                flash="Le titre est obligatoire (et le référentiel, s'il est choisi, doit être valide).",
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

    @staticmethod
    def supprimer(request: Request) -> Response:
        scenario_id = parse_id(request.route("id"))
        if scenario_id is None:
            return BaseController.not_found()
        scenario = get_scenario(scenario_id)
        if scenario is None:
            return BaseController.not_found()
        # Un scénario « utilisé » par des élèves est verrouillé (comme pour le
        # recalcul de statut) : sa suppression casserait en cascade des données de
        # suivi. On refuse côté serveur, en plus de masquer le bouton côté liste.
        if scenario.get("Statut") == "utilise":
            return BaseController.redirect_with_flash(
                request, "/conception/scenario",
                "Ce scénario est utilisé : il ne peut pas être supprimé.", "error",
            )
        titre = str(scenario.get("Titre") or "")
        supprimer_scenario(scenario_id)
        return BaseController.redirect_with_flash(
            request, "/conception/scenario",
            f"Scénario « {titre} » supprimé.", "success",
        )

    # ── Vue principale ───────────────────────────────────────────────────────

    @staticmethod
    def editeur(request: Request) -> Response:
        scenario_id = parse_id(request.route("id"))
        if scenario_id is None:
            return BaseController.not_found()
        scenario = get_scenario(scenario_id)
        if scenario is None:
            return BaseController.not_found()
        # Auto-réparation du statut de la séquence appariée (dérivé persisté) :
        # l'arbre « Famille pédagogique » l'affiche et en dérive la ligne
        # « Ajouter une séance » (garde ADR-034).
        sequence_appairee = get_sequence_appairee(scenario_id)
        if sequence_appairee is not None:
            recalculer_statut_sequence(int(sequence_appairee["Id"]))

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
            # Verrou du référentiel : plus de rattachement une fois la paire
            # (scénario ou séquence) finalisée.
            "referentiel_verrouille": paire_est_finalisee(scenario_id),
            # Arbre de navigation (ADR-029) : séquence appairée (tronc) et ses
            # séances (feuilles), affichés sous le corps du tunnel.
            **contexte_famille(scenario),
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
            frais = cast("dict[str, Any]", get_scenario(scenario_id))
            return BaseController.render(
                "app/scenario_editeur/_feedback_ecriture.html",
                context={**contexte_famille(frais), **contexte_stepper(frais, "titre")},
                request=request,
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
            frais = cast("dict[str, Any]", get_scenario(scenario_id))
            return BaseController.render(
                "app/scenario_editeur/_feedback_ecriture.html",
                context={**contexte_famille(frais), **contexte_stepper(frais, "contexte")},
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
        # Verrou : le référentiel ne change plus une fois la paire finalisée.
        if paire_est_finalisee(scenario_id):
            return BaseController.redirect(
                f"/conception/scenario/{scenario_id}", request=request,
                flash="Le référentiel est verrouillé : le scénario ou sa séquence est finalisé.",
            )
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

    # ── Export : PDF, Markdown, JSON (ADR-024) ───────────────────────────────

    @staticmethod
    def _telecharger(
        request: Request, extension: str, mime: str,
        construire: "Callable[[int], bytes | str]",
    ) -> Response:
        """Télécharge un export du scénario. Réservé aux scénarios finalisés (ou
        déjà utilisés : contenu complet et figé)."""
        scenario_id = parse_id(request.route("id"))
        if scenario_id is None:
            return BaseController.not_found()
        scenario = get_scenario(scenario_id)
        if scenario is None:
            return BaseController.not_found()
        if scenario.get("Statut") not in ("finalise", "utilise"):
            return BaseController.redirect_with_flash(
                request,
                f"/conception/scenario/{scenario_id}?etape=titre",
                "L'export n'est disponible que pour un scénario finalisé.",
                "error",
            )
        nom = slug(str(scenario.get("Titre") or "scenario"))
        return Response(
            200,
            construire(scenario_id),
            mime,
            headers={"Content-Disposition": f'attachment; filename="scenario-{nom}.{extension}"'},
        )

    @staticmethod
    def telecharger_pdf(request: Request) -> Response:
        return ScenarioEditeurController._telecharger(
            request, "pdf", "application/pdf", construire_pdf
        )

    @staticmethod
    def telecharger_md(request: Request) -> Response:
        return ScenarioEditeurController._telecharger(
            request, "md", "text/markdown; charset=utf-8", construire_markdown
        )

    @staticmethod
    def telecharger_json(request: Request) -> Response:
        return ScenarioEditeurController._telecharger(
            request, "json", "application/json; charset=utf-8", construire_json
        )
