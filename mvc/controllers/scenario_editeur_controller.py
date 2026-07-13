# pyright: strict
"""Éditeur de scénario (ADR-019) : conception sur mesure, alignée cpro-education.

Interface principale de conception d'un scénario, en 4 sections (Titre, Contexte,
Liaison avec le référentiel, Ressources), remplaçant le CRUD plat. Phase 1 : la
section Titre (titre, co-intervention, co-auteurs). La Liaison consommera l'arbre
de l'atelier référentiel (ADR-018).
"""
from typing import Any, cast

from core.http.request import Request
from core.http.response import Response
from core.mvc.controller.base_controller import BaseController

from forge_mvc_files import UploadError, delete_upload, save_upload

from mvc.models.referentiel_atelier_model import get_arbre, list_referentiels
from mvc.models.scenario_editeur_model import (
    ajouter_ressource,
    creer_scenario,
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
    list_ressources,
    list_scenarios,
    supprimer_ressource,
)


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
            context={"scenarios": list_scenarios()},
            request=request,
        )

    @staticmethod
    def nouveau(request: Request) -> Response:
        titre = request.form("titre", "").strip()
        if not titre:
            return BaseController.redirect("/conception/scenario")
        scenario_id = creer_scenario(titre)
        return BaseController.redirect(f"/conception/scenario/{scenario_id}")

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
        return BaseController.render(
            "app/scenario_editeur/editeur.html",
            context={
                "scenario": scenario,
                "co_auteur_ids": get_co_auteur_ids(scenario_id),
                "professeurs": list_professeurs(),
                "referentiels": list_referentiels(),
                "arbre": arbre,
                "activite_ids": get_activite_ids(scenario_id),
                "critere_ids": get_critere_ids(scenario_id),
                "ressources": list_ressources(scenario_id),
            },
            request=request,
        )

    @staticmethod
    def enregistrer_titre(request: Request) -> Response:
        scenario_id = ScenarioEditeurController._parse_id(request.route("id"))
        if scenario_id is None:
            return BaseController.not_found()
        if get_scenario(scenario_id) is None:
            return BaseController.not_found()
        titre = request.form("titre", "").strip()
        co_intervention = request.form("co_intervention", "") != ""
        co_auteur_ids = ScenarioEditeurController._parse_many_ids(request, "co_auteurs")
        enregistrer_titre(scenario_id, titre, co_intervention, co_auteur_ids)
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
        return BaseController.redirect(
            f"/conception/scenario/{scenario_id}", request=request, flash="Liaison au référentiel enregistrée."
        )

    @staticmethod
    def uploader_ressource(request: Request) -> Response:
        scenario_id = ScenarioEditeurController._parse_id(request.route("id"))
        if scenario_id is None or get_scenario(scenario_id) is None:
            return BaseController.not_found()
        cible = f"/conception/scenario/{scenario_id}"
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
            request, f"/conception/scenario/{scenario_id}", "Ressource supprimée.", "success"
        )
