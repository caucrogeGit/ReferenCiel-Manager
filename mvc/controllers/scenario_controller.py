import csv
import io
from core.http.request import Request
from core.http.response import Response
from core.mvc.controller import BaseController
from core.mvc.view.pagination import Pagination
from mvc.models.scenario_model import (
    get_scenario_by_id, add_scenario, update_scenario, delete_scenario, bulk_delete_scenarios,
    count_scenarios, find_scenarios_paginated, find_scenarios_for_export,
    get_referentiel_niveau_classe_choices, get_professeur_choices, get_competence_choices, get_critere_observable_choices,
    get_scenario_competence_ids, add_scenario_competence_ids, sync_scenario_competence_ids, get_scenario_competence_labels_by_scenario_id, get_scenario_competence_labels, get_scenario_critere_observable_ids, add_scenario_critere_observable_ids, sync_scenario_critere_observable_ids, get_scenario_critere_observable_labels_by_scenario_id, get_scenario_critere_observable_labels,
)
from mvc.forms.scenario_form import ScenarioForm
from core.security.session import get_flash, get_session_id


def _form_data_from_scenario(record: dict) -> dict:
    """Convertit les colonnes SQL vers les noms de champs du formulaire."""
    return {
        "titre": record.get("Titre"),
        "intention": record.get("Intention"),
        "objectifs": record.get("Objectifs"),
        "statut": record.get("Statut"),
        "version": record.get("Version"),
        "referentiel_id": record.get("referentiel_id"),
        "auteur_id": record.get("auteur_id"),
        "created_at": record.get("CreatedAt"),
        "updated_at": record.get("UpdatedAt"),
    }


def _scenario_form_options():
    return {
        "referentiel_id_choices": get_referentiel_niveau_classe_choices(),
        "auteur_id_choices": get_professeur_choices(),
    }


def _query_param(request, name, default=""):
    """Retourne le premier paramètre GET, au format parse_qs de Forge."""
    values = request.params.get(name, [default])
    return values[0] if values else default


def _is_hx_request(request):
    """Détecte une requête HTMX locale au CRUD généré."""
    return request.headers.get("HX-Request", "").lower() == "true"


_CSV_COLS = [('Titre', 'Titre'), ('Intention', 'Intention'), ('Objectifs', 'Objectifs'), ('Statut', 'Statut'), ('Version', 'Version'), ('Referentiel id', 'referentiel_id_label'), ('Auteur id', 'auteur_id_label'), ('Created at', 'CreatedAt'), ('Updated at', 'UpdatedAt')]


class ScenarioController(BaseController):

    @staticmethod
    def _parse_id(value):
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _parse_bulk_ids(request):
        """Extrait, valide et déduplique les IDs du formulaire de suppression groupée."""
        raw = request.body.get("ids", [])
        if isinstance(raw, str):
            raw = [raw]
        valid = []
        seen = set()
        for v in (raw or []):
            try:
                item = int(v)
            except (TypeError, ValueError):
                continue
            if item <= 0 or item in seen:
                continue
            seen.add(item)
            valid.append(item)
        return valid

    @staticmethod
    def _parse_many_ids(request, field_name):
        raw = request.body.get(field_name, [])
        values = raw if isinstance(raw, list) else ([raw] if raw else [])
        selected = []
        seen = set()
        for value in values:
            try:
                item = int(value)
            except (TypeError, ValueError):
                continue
            if item <= 0 or item in seen:
                continue
            seen.add(item)
            selected.append(item)
        return selected

    @staticmethod
    def _list_context(request):
        q         = _query_param(request, "q").strip()
        sort      = _query_param(request, "sort")
        if sort not in {"titre", "intention", "objectifs", "statut", "version", "referentiel_id", "auteur_id", "created_at", "updated_at", "id"}:
            sort = ""
        direction = _query_param(request, "direction", "desc")
        if direction not in ("asc", "desc"):
            direction = "asc"
        limit  = 20
        referentiel_id_raw = _query_param(request, "referentiel_id").strip()
        referentiel_id_f = ""
        if referentiel_id_raw:
            try:
                referentiel_id_f = int(referentiel_id_raw)
            except (TypeError, ValueError):
                referentiel_id_f = ""
        auteur_id_raw = _query_param(request, "auteur_id").strip()
        auteur_id_f = ""
        if auteur_id_raw:
            try:
                auteur_id_f = int(auteur_id_raw)
            except (TypeError, ValueError):
                auteur_id_f = ""
        relation_filters = {}
        relation_filters["referentiel_id"] = {"options": [{"id": value, "label": label} for value, label in get_referentiel_niveau_classe_choices()]}
        relation_filters["auteur_id"] = {"options": [{"id": value, "label": label} for value, label in get_professeur_choices()]}
        _filters = {}
        if referentiel_id_f != "":
            _filters["referentiel_id"] = referentiel_id_f
        if auteur_id_f != "":
            _filters["auteur_id"] = auteur_id_f
        total    = count_scenarios(q or None, filters=_filters or None)
        pagination_state = Pagination(request, total, limit)
        limit = pagination_state.limit
        offset = pagination_state.offset
        empty_context = "search_filters" if q and _filters else ("search" if q else ("filters" if _filters else None))
        scenarios = find_scenarios_paginated(
            q=q or None, sort=sort or None, direction=direction,
            limit=limit, offset=offset, filters=_filters or None,
        )
        pagination = pagination_state.to_dict()
        pagination.update({
            "q": q, "sort": sort, "direction": direction,
            "filters": {"referentiel_id": referentiel_id_f, "auteur_id": auteur_id_f},
        })
        return {
                "scenarios": scenarios,
                "pagination": pagination,
                "empty_context": empty_context,
                "relation_filters": relation_filters,
                "flash": get_flash(get_session_id(request)),
                "competences_by_scenario_id": get_scenario_competence_labels_by_scenario_id([row["Id"] for row in scenarios]),
                "critere_observables_by_scenario_id": get_scenario_critere_observable_labels_by_scenario_id([row["Id"] for row in scenarios]),
            }

    @staticmethod
    def index(request: Request) -> Response:
        context = ScenarioController._list_context(request)
        template = "app/scenario/_results.html" if _is_hx_request(request) else "app/scenario/index.html"
        return BaseController.render(template, context=context, request=request)

    @staticmethod
    def new(request: Request) -> Response:
        form = ScenarioForm(**_scenario_form_options())
        return BaseController.render("app/scenario/form.html",
            context={
                "form": form,
                "action": "/scenario/create",
                "titre": "Nouveau scenario",
                "competence_choices": get_competence_choices(),
                "competence_ids_selected": [],
                "critere_observable_choices": get_critere_observable_choices(),
                "critere_observable_ids_selected": [],
            },
            request=request)

    @staticmethod
    def create(request: Request) -> Response:
        form = ScenarioForm.from_request(request, **_scenario_form_options())
        competence_ids = ScenarioController._parse_many_ids(request, "competence_ids")
        critere_observable_ids = ScenarioController._parse_many_ids(request, "critere_observable_ids")
        if not form.is_valid():
            return BaseController.validation_error("app/scenario/form.html",
                context={
                    "form": form,
                    "action": "/scenario/create",
                    "titre": "Nouveau scenario",
                    "competence_choices": get_competence_choices(),
                    "competence_ids_selected": competence_ids,
                    "critere_observable_choices": get_critere_observable_choices(),
                    "critere_observable_ids_selected": critere_observable_ids,
                },
                request=request)
        created_id = add_scenario(form.cleaned_data)
        add_scenario_competence_ids(created_id, competence_ids)
        add_scenario_critere_observable_ids(created_id, critere_observable_ids)
        return BaseController.redirect_with_flash(request, "/scenario", "Scenario créé.")

    @staticmethod
    def show(request: Request) -> Response:
        id = ScenarioController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        scenario = get_scenario_by_id(id)
        if scenario is None:
            return BaseController.not_found()
        competence_labels = get_scenario_competence_labels(id)
        critere_observable_labels = get_scenario_critere_observable_labels(id)
        return BaseController.render("app/scenario/show.html",
            context={"scenario": scenario, "flash": get_flash(get_session_id(request)), "competence_labels": competence_labels, "critere_observable_labels": critere_observable_labels},
            request=request)

    @staticmethod
    def edit(request: Request) -> Response:
        id = ScenarioController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        scenario = get_scenario_by_id(id)
        if scenario is None:
            return BaseController.not_found()
        return BaseController.render("app/scenario/form.html",
            context={
                "form": ScenarioForm(_form_data_from_scenario(scenario), **_scenario_form_options()),
                "action": f"/scenario/update/{id}",
                "titre": "Modifier scenario",
                "competence_choices": get_competence_choices(),
                "competence_ids_selected": get_scenario_competence_ids(id),
                "critere_observable_choices": get_critere_observable_choices(),
                "critere_observable_ids_selected": get_scenario_critere_observable_ids(id),
            },
            request=request)

    @staticmethod
    def update(request: Request) -> Response:
        id = ScenarioController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        form = ScenarioForm.from_request(request, **_scenario_form_options())
        competence_ids = ScenarioController._parse_many_ids(request, "competence_ids")
        critere_observable_ids = ScenarioController._parse_many_ids(request, "critere_observable_ids")
        if not form.is_valid():
            return BaseController.validation_error("app/scenario/form.html",
                context={
                    "form": form,
                    "action": f"/scenario/update/{id}",
                    "titre": "Modifier scenario",
                    "competence_choices": get_competence_choices(),
                    "competence_ids_selected": competence_ids,
                    "critere_observable_choices": get_critere_observable_choices(),
                    "critere_observable_ids_selected": critere_observable_ids,
                },
                request=request)
        update_scenario(id, form.cleaned_data)
        sync_scenario_competence_ids(id, competence_ids)
        sync_scenario_critere_observable_ids(id, critere_observable_ids)
        return BaseController.redirect_with_flash(
            request, f"/scenario/show/{id}", "Scenario mis à jour.")

    @staticmethod
    def destroy(request: Request) -> Response:
        id = ScenarioController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        delete_scenario(id)
        if _is_hx_request(request):
            context = ScenarioController._list_context(request)
            return BaseController.render("app/scenario/_results.html", context=context, request=request)
        return BaseController.redirect_with_flash(request, "/scenario", "Scenario supprimé.")


    @staticmethod
    def bulk_delete(request: Request) -> Response:
        ids = ScenarioController._parse_bulk_ids(request)
        if not ids:
            return BaseController.redirect_with_flash(request, "/scenario", "Aucun élément sélectionné.")
        return BaseController.render("app/scenario/bulk_delete_confirm.html",
            context={"ids": ids, "count": len(ids), "flash": get_flash(get_session_id(request))},
            request=request)

    @staticmethod
    def bulk_delete_confirm(request: Request) -> Response:
        ids = ScenarioController._parse_bulk_ids(request)
        if not ids:
            return BaseController.redirect_with_flash(request, "/scenario", "Aucun élément sélectionné.")
        bulk_delete_scenarios(ids)
        count = len(ids)
        return BaseController.redirect_with_flash(
            request, "/scenario",
            f"{count} élément(s) supprimé(s).")


    @staticmethod
    def _csv_escape(value: str) -> str:
        if value and value[0] in ("=", "+", "-", "@"):
            return "'" + value
        return value

    @staticmethod
    def export_csv(request: Request) -> Response:
        q = _query_param(request, "q").strip()
        sort = _query_param(request, "sort")
        if sort not in {"titre", "intention", "objectifs", "statut", "version", "referentiel_id", "auteur_id", "created_at", "updated_at", "id"}:
            sort = ""
        direction = _query_param(request, "direction", "desc")
        if direction not in ("asc", "desc"):
            direction = "asc"
        referentiel_id_raw = _query_param(request, "referentiel_id").strip()
        referentiel_id_f = ""
        if referentiel_id_raw:
            try:
                referentiel_id_f = int(referentiel_id_raw)
            except (TypeError, ValueError):
                referentiel_id_f = ""
        auteur_id_raw = _query_param(request, "auteur_id").strip()
        auteur_id_f = ""
        if auteur_id_raw:
            try:
                auteur_id_f = int(auteur_id_raw)
            except (TypeError, ValueError):
                auteur_id_f = ""
        _filters = {}
        if referentiel_id_f != "":
            _filters["referentiel_id"] = referentiel_id_f
        if auteur_id_f != "":
            _filters["auteur_id"] = auteur_id_f
        rows = find_scenarios_for_export(q=q or None, sort=sort or None, direction=direction, filters=_filters or None)
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_ALL)
        writer.writerow([header for header, _ in _CSV_COLS])
        for row in rows:
            writer.writerow([ScenarioController._csv_escape(str(row.get(key) or "")) for _, key in _CSV_COLS])
        content = output.getvalue().encode("utf-8")
        return Response(
            200,
            content,
            "text/csv; charset=utf-8",
            headers={
                "Content-Disposition": 'attachment; filename="scenarios.csv"',
                "Cache-Control": "no-store",
            },
        )
