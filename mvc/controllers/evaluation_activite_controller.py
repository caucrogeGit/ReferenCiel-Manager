import csv
import io
from core.http.request import Request
from core.http.response import Response
from core.mvc.controller import BaseController
from core.mvc.view.pagination import Pagination
from mvc.models.evaluation_activite_model import (
    get_evaluation_activite_by_id, add_evaluation_activite, update_evaluation_activite, delete_evaluation_activite, bulk_delete_evaluation_activites,
    count_evaluation_activites, find_evaluation_activites_paginated, find_evaluation_activites_for_export,
    get_progression_palier_choices, get_activite_choices, get_professeur_choices,
)
from mvc.forms.evaluation_activite_form import EvaluationActiviteForm
from core.security.session import get_flash, get_session_id


def _form_data_from_evaluation_activite(record: dict) -> dict:
    """Convertit les colonnes SQL vers les noms de champs du formulaire."""
    return {
        "date_evaluation": record.get("DateEvaluation"),
        "appreciation": record.get("Appreciation"),
        "progression_palier_id": record.get("progression_palier_id"),
        "activite_id": record.get("activite_id"),
        "professeur_id": record.get("professeur_id"),
        "created_at": record.get("CreatedAt"),
        "updated_at": record.get("UpdatedAt"),
    }


def _evaluation_activite_form_options():
    return {
        "progression_palier_id_choices": get_progression_palier_choices(),
        "activite_id_choices": get_activite_choices(),
        "professeur_id_choices": get_professeur_choices(),
    }


def _query_param(request, name, default=""):
    """Retourne le premier paramètre GET, au format parse_qs de Forge."""
    values = request.params.get(name, [default])
    return values[0] if values else default


def _is_hx_request(request):
    """Détecte une requête HTMX locale au CRUD généré."""
    return request.headers.get("HX-Request", "").lower() == "true"


_CSV_COLS = [('Date evaluation', 'DateEvaluation'), ('Appreciation', 'Appreciation'), ('Progression séance', 'progression_palier_id_label'), ('Activite id', 'activite_id_label'), ('Professeur id', 'professeur_id_label'), ('Created at', 'CreatedAt'), ('Updated at', 'UpdatedAt')]


class EvaluationActiviteController(BaseController):

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
    def _list_context(request):
        q         = _query_param(request, "q").strip()
        sort      = _query_param(request, "sort")
        if sort not in {"date_evaluation", "appreciation", "progression_palier_id", "activite_id", "professeur_id", "created_at", "updated_at", "id"}:
            sort = ""
        direction = _query_param(request, "direction", "desc")
        if direction not in ("asc", "desc"):
            direction = "asc"
        limit  = 20
        progression_palier_id_raw = _query_param(request, "progression_palier_id").strip()
        progression_palier_id_f = ""
        if progression_palier_id_raw:
            try:
                progression_palier_id_f = int(progression_palier_id_raw)
            except (TypeError, ValueError):
                progression_palier_id_f = ""
        activite_id_raw = _query_param(request, "activite_id").strip()
        activite_id_f = ""
        if activite_id_raw:
            try:
                activite_id_f = int(activite_id_raw)
            except (TypeError, ValueError):
                activite_id_f = ""
        professeur_id_raw = _query_param(request, "professeur_id").strip()
        professeur_id_f = ""
        if professeur_id_raw:
            try:
                professeur_id_f = int(professeur_id_raw)
            except (TypeError, ValueError):
                professeur_id_f = ""
        relation_filters = {}
        relation_filters["progression_palier_id"] = {"options": [{"id": value, "label": label} for value, label in get_progression_palier_choices()]}
        relation_filters["activite_id"] = {"options": [{"id": value, "label": label} for value, label in get_activite_choices()]}
        relation_filters["professeur_id"] = {"options": [{"id": value, "label": label} for value, label in get_professeur_choices()]}
        _filters = {}
        if progression_palier_id_f != "":
            _filters["progression_palier_id"] = progression_palier_id_f
        if activite_id_f != "":
            _filters["activite_id"] = activite_id_f
        if professeur_id_f != "":
            _filters["professeur_id"] = professeur_id_f
        total    = count_evaluation_activites(q or None, filters=_filters or None)
        pagination_state = Pagination(request, total, limit)
        limit = pagination_state.limit
        offset = pagination_state.offset
        empty_context = "search_filters" if q and _filters else ("search" if q else ("filters" if _filters else None))
        evaluation_activites = find_evaluation_activites_paginated(
            q=q or None, sort=sort or None, direction=direction,
            limit=limit, offset=offset, filters=_filters or None,
        )
        pagination = pagination_state.to_dict()
        pagination.update({
            "q": q, "sort": sort, "direction": direction,
            "filters": {"progression_palier_id": progression_palier_id_f, "activite_id": activite_id_f, "professeur_id": professeur_id_f},
        })
        return {
                "evaluation_activites": evaluation_activites,
                "pagination": pagination,
                "empty_context": empty_context,
                "relation_filters": relation_filters,
                "flash": get_flash(get_session_id(request)),
            }

    @staticmethod
    def index(request: Request) -> Response:
        context = EvaluationActiviteController._list_context(request)
        template = "app/evaluation_activite/_results.html" if _is_hx_request(request) else "app/evaluation_activite/index.html"
        return BaseController.render(template, context=context, request=request)

    @staticmethod
    def new(request: Request) -> Response:
        form = EvaluationActiviteForm(**_evaluation_activite_form_options())
        return BaseController.render("app/evaluation_activite/form.html",
            context={
                "form": form,
                "action": "/evaluation_activite/create",
                "titre": "Nouveau evaluation_activite",
            },
            request=request)

    @staticmethod
    def create(request: Request) -> Response:
        form = EvaluationActiviteForm.from_request(request, **_evaluation_activite_form_options())
        if not form.is_valid():
            return BaseController.validation_error("app/evaluation_activite/form.html",
                context={
                    "form": form,
                    "action": "/evaluation_activite/create",
                    "titre": "Nouveau evaluation_activite",
                },
                request=request)
        add_evaluation_activite(form.cleaned_data)
        return BaseController.redirect_with_flash(request, "/evaluation_activite", "EvaluationActivite créé.")

    @staticmethod
    def show(request: Request) -> Response:
        id = EvaluationActiviteController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        evaluation_activite = get_evaluation_activite_by_id(id)
        if evaluation_activite is None:
            return BaseController.not_found()
        return BaseController.render("app/evaluation_activite/show.html",
            context={"evaluation_activite": evaluation_activite, "flash": get_flash(get_session_id(request))},
            request=request)

    @staticmethod
    def edit(request: Request) -> Response:
        id = EvaluationActiviteController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        evaluation_activite = get_evaluation_activite_by_id(id)
        if evaluation_activite is None:
            return BaseController.not_found()
        return BaseController.render("app/evaluation_activite/form.html",
            context={
                "form": EvaluationActiviteForm(_form_data_from_evaluation_activite(evaluation_activite), **_evaluation_activite_form_options()),
                "action": f"/evaluation_activite/update/{id}",
                "titre": "Modifier evaluation_activite",
            },
            request=request)

    @staticmethod
    def update(request: Request) -> Response:
        id = EvaluationActiviteController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        form = EvaluationActiviteForm.from_request(request, **_evaluation_activite_form_options())
        if not form.is_valid():
            return BaseController.validation_error("app/evaluation_activite/form.html",
                context={
                    "form": form,
                    "action": f"/evaluation_activite/update/{id}",
                    "titre": "Modifier evaluation_activite",
                },
                request=request)
        update_evaluation_activite(id, form.cleaned_data)
        return BaseController.redirect_with_flash(
            request, f"/evaluation_activite/show/{id}", "EvaluationActivite mis à jour.")

    @staticmethod
    def destroy(request: Request) -> Response:
        id = EvaluationActiviteController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        delete_evaluation_activite(id)
        if _is_hx_request(request):
            context = EvaluationActiviteController._list_context(request)
            return BaseController.render("app/evaluation_activite/_results.html", context=context, request=request)
        return BaseController.redirect_with_flash(request, "/evaluation_activite", "EvaluationActivite supprimé.")


    @staticmethod
    def bulk_delete(request: Request) -> Response:
        ids = EvaluationActiviteController._parse_bulk_ids(request)
        if not ids:
            return BaseController.redirect_with_flash(request, "/evaluation_activite", "Aucun élément sélectionné.")
        return BaseController.render("app/evaluation_activite/bulk_delete_confirm.html",
            context={"ids": ids, "count": len(ids), "flash": get_flash(get_session_id(request))},
            request=request)

    @staticmethod
    def bulk_delete_confirm(request: Request) -> Response:
        ids = EvaluationActiviteController._parse_bulk_ids(request)
        if not ids:
            return BaseController.redirect_with_flash(request, "/evaluation_activite", "Aucun élément sélectionné.")
        bulk_delete_evaluation_activites(ids)
        count = len(ids)
        return BaseController.redirect_with_flash(
            request, "/evaluation_activite",
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
        if sort not in {"date_evaluation", "appreciation", "progression_palier_id", "activite_id", "professeur_id", "created_at", "updated_at", "id"}:
            sort = ""
        direction = _query_param(request, "direction", "desc")
        if direction not in ("asc", "desc"):
            direction = "asc"
        progression_palier_id_raw = _query_param(request, "progression_palier_id").strip()
        progression_palier_id_f = ""
        if progression_palier_id_raw:
            try:
                progression_palier_id_f = int(progression_palier_id_raw)
            except (TypeError, ValueError):
                progression_palier_id_f = ""
        activite_id_raw = _query_param(request, "activite_id").strip()
        activite_id_f = ""
        if activite_id_raw:
            try:
                activite_id_f = int(activite_id_raw)
            except (TypeError, ValueError):
                activite_id_f = ""
        professeur_id_raw = _query_param(request, "professeur_id").strip()
        professeur_id_f = ""
        if professeur_id_raw:
            try:
                professeur_id_f = int(professeur_id_raw)
            except (TypeError, ValueError):
                professeur_id_f = ""
        _filters = {}
        if progression_palier_id_f != "":
            _filters["progression_palier_id"] = progression_palier_id_f
        if activite_id_f != "":
            _filters["activite_id"] = activite_id_f
        if professeur_id_f != "":
            _filters["professeur_id"] = professeur_id_f
        rows = find_evaluation_activites_for_export(q=q or None, sort=sort or None, direction=direction, filters=_filters or None)
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_ALL)
        writer.writerow([header for header, _ in _CSV_COLS])
        for row in rows:
            writer.writerow([EvaluationActiviteController._csv_escape(str(row.get(key) or "")) for _, key in _CSV_COLS])
        content = output.getvalue().encode("utf-8")
        return Response(
            200,
            content,
            "text/csv; charset=utf-8",
            headers={
                "Content-Disposition": 'attachment; filename="evaluation_activites.csv"',
                "Cache-Control": "no-store",
            },
        )
