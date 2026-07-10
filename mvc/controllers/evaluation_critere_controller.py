import csv
import io
from core.http.request import Request
from core.http.response import Response
from core.mvc.controller import BaseController
from core.mvc.view.pagination import Pagination
from mvc.models.evaluation_critere_model import (
    get_evaluation_critere_by_id, add_evaluation_critere, update_evaluation_critere, delete_evaluation_critere, bulk_delete_evaluation_criteres,
    count_evaluation_criteres, find_evaluation_criteres_paginated, find_evaluation_criteres_for_export,
    get_evaluation_activite_choices, get_critere_observable_choices,
)
from mvc.forms.evaluation_critere_form import EvaluationCritereForm
from core.security.session import get_flash, get_session_id


def _form_data_from_evaluation_critere(record: dict) -> dict:
    """Convertit les colonnes SQL vers les noms de champs du formulaire."""
    return {
        "niveau": record.get("Niveau"),
        "evaluation_activite_id": record.get("evaluation_activite_id"),
        "critere_id": record.get("critere_id"),
        "created_at": record.get("CreatedAt"),
        "updated_at": record.get("UpdatedAt"),
    }


def _evaluation_critere_form_options():
    return {
        "evaluation_activite_id_choices": get_evaluation_activite_choices(),
        "critere_id_choices": get_critere_observable_choices(),
    }


def _query_param(request, name, default=""):
    """Retourne le premier paramètre GET, au format parse_qs de Forge."""
    values = request.params.get(name, [default])
    return values[0] if values else default


def _is_hx_request(request):
    """Détecte une requête HTMX locale au CRUD généré."""
    return request.headers.get("HX-Request", "").lower() == "true"


_CSV_COLS = [('Niveau', 'Niveau'), ('Evaluation activite id', 'evaluation_activite_id_label'), ('Critere id', 'critere_id_label'), ('Created at', 'CreatedAt'), ('Updated at', 'UpdatedAt')]


class EvaluationCritereController(BaseController):

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
        if sort not in {"niveau", "evaluation_activite_id", "critere_id", "created_at", "updated_at", "id"}:
            sort = ""
        direction = _query_param(request, "direction", "desc")
        if direction not in ("asc", "desc"):
            direction = "asc"
        limit  = 20
        evaluation_activite_id_raw = _query_param(request, "evaluation_activite_id").strip()
        evaluation_activite_id_f = ""
        if evaluation_activite_id_raw:
            try:
                evaluation_activite_id_f = int(evaluation_activite_id_raw)
            except (TypeError, ValueError):
                evaluation_activite_id_f = ""
        critere_id_raw = _query_param(request, "critere_id").strip()
        critere_id_f = ""
        if critere_id_raw:
            try:
                critere_id_f = int(critere_id_raw)
            except (TypeError, ValueError):
                critere_id_f = ""
        relation_filters = {}
        relation_filters["evaluation_activite_id"] = {"options": [{"id": value, "label": label} for value, label in get_evaluation_activite_choices()]}
        relation_filters["critere_id"] = {"options": [{"id": value, "label": label} for value, label in get_critere_observable_choices()]}
        _filters = {}
        if evaluation_activite_id_f != "":
            _filters["evaluation_activite_id"] = evaluation_activite_id_f
        if critere_id_f != "":
            _filters["critere_id"] = critere_id_f
        total    = count_evaluation_criteres(q or None, filters=_filters or None)
        pagination_state = Pagination(request, total, limit)
        limit = pagination_state.limit
        offset = pagination_state.offset
        empty_context = "search_filters" if q and _filters else ("search" if q else ("filters" if _filters else None))
        evaluation_criteres = find_evaluation_criteres_paginated(
            q=q or None, sort=sort or None, direction=direction,
            limit=limit, offset=offset, filters=_filters or None,
        )
        pagination = pagination_state.to_dict()
        pagination.update({
            "q": q, "sort": sort, "direction": direction,
            "filters": {"evaluation_activite_id": evaluation_activite_id_f, "critere_id": critere_id_f},
        })
        return {
                "evaluation_criteres": evaluation_criteres,
                "pagination": pagination,
                "empty_context": empty_context,
                "relation_filters": relation_filters,
                "flash": get_flash(get_session_id(request)),
            }

    @staticmethod
    def index(request: Request) -> Response:
        context = EvaluationCritereController._list_context(request)
        template = "app/evaluation_critere/_results.html" if _is_hx_request(request) else "app/evaluation_critere/index.html"
        return BaseController.render(template, context=context, request=request)

    @staticmethod
    def new(request: Request) -> Response:
        form = EvaluationCritereForm(**_evaluation_critere_form_options())
        return BaseController.render("app/evaluation_critere/form.html",
            context={
                "form": form,
                "action": "/evaluation_critere/create",
                "titre": "Nouveau evaluation_critere",
            },
            request=request)

    @staticmethod
    def create(request: Request) -> Response:
        form = EvaluationCritereForm.from_request(request, **_evaluation_critere_form_options())
        if not form.is_valid():
            return BaseController.validation_error("app/evaluation_critere/form.html",
                context={
                    "form": form,
                    "action": "/evaluation_critere/create",
                    "titre": "Nouveau evaluation_critere",
                },
                request=request)
        add_evaluation_critere(form.cleaned_data)
        return BaseController.redirect_with_flash(request, "/evaluation_critere", "EvaluationCritere créé.")

    @staticmethod
    def show(request: Request) -> Response:
        id = EvaluationCritereController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        evaluation_critere = get_evaluation_critere_by_id(id)
        if evaluation_critere is None:
            return BaseController.not_found()
        return BaseController.render("app/evaluation_critere/show.html",
            context={"evaluation_critere": evaluation_critere, "flash": get_flash(get_session_id(request))},
            request=request)

    @staticmethod
    def edit(request: Request) -> Response:
        id = EvaluationCritereController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        evaluation_critere = get_evaluation_critere_by_id(id)
        if evaluation_critere is None:
            return BaseController.not_found()
        return BaseController.render("app/evaluation_critere/form.html",
            context={
                "form": EvaluationCritereForm(_form_data_from_evaluation_critere(evaluation_critere), **_evaluation_critere_form_options()),
                "action": f"/evaluation_critere/update/{id}",
                "titre": "Modifier evaluation_critere",
            },
            request=request)

    @staticmethod
    def update(request: Request) -> Response:
        id = EvaluationCritereController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        form = EvaluationCritereForm.from_request(request, **_evaluation_critere_form_options())
        if not form.is_valid():
            return BaseController.validation_error("app/evaluation_critere/form.html",
                context={
                    "form": form,
                    "action": f"/evaluation_critere/update/{id}",
                    "titre": "Modifier evaluation_critere",
                },
                request=request)
        update_evaluation_critere(id, form.cleaned_data)
        return BaseController.redirect_with_flash(
            request, f"/evaluation_critere/show/{id}", "EvaluationCritere mis à jour.")

    @staticmethod
    def destroy(request: Request) -> Response:
        id = EvaluationCritereController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        delete_evaluation_critere(id)
        if _is_hx_request(request):
            context = EvaluationCritereController._list_context(request)
            return BaseController.render("app/evaluation_critere/_results.html", context=context, request=request)
        return BaseController.redirect_with_flash(request, "/evaluation_critere", "EvaluationCritere supprimé.")


    @staticmethod
    def bulk_delete(request: Request) -> Response:
        ids = EvaluationCritereController._parse_bulk_ids(request)
        if not ids:
            return BaseController.redirect_with_flash(request, "/evaluation_critere", "Aucun élément sélectionné.")
        return BaseController.render("app/evaluation_critere/bulk_delete_confirm.html",
            context={"ids": ids, "count": len(ids), "flash": get_flash(get_session_id(request))},
            request=request)

    @staticmethod
    def bulk_delete_confirm(request: Request) -> Response:
        ids = EvaluationCritereController._parse_bulk_ids(request)
        if not ids:
            return BaseController.redirect_with_flash(request, "/evaluation_critere", "Aucun élément sélectionné.")
        bulk_delete_evaluation_criteres(ids)
        count = len(ids)
        return BaseController.redirect_with_flash(
            request, "/evaluation_critere",
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
        if sort not in {"niveau", "evaluation_activite_id", "critere_id", "created_at", "updated_at", "id"}:
            sort = ""
        direction = _query_param(request, "direction", "desc")
        if direction not in ("asc", "desc"):
            direction = "asc"
        evaluation_activite_id_raw = _query_param(request, "evaluation_activite_id").strip()
        evaluation_activite_id_f = ""
        if evaluation_activite_id_raw:
            try:
                evaluation_activite_id_f = int(evaluation_activite_id_raw)
            except (TypeError, ValueError):
                evaluation_activite_id_f = ""
        critere_id_raw = _query_param(request, "critere_id").strip()
        critere_id_f = ""
        if critere_id_raw:
            try:
                critere_id_f = int(critere_id_raw)
            except (TypeError, ValueError):
                critere_id_f = ""
        _filters = {}
        if evaluation_activite_id_f != "":
            _filters["evaluation_activite_id"] = evaluation_activite_id_f
        if critere_id_f != "":
            _filters["critere_id"] = critere_id_f
        rows = find_evaluation_criteres_for_export(q=q or None, sort=sort or None, direction=direction, filters=_filters or None)
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_ALL)
        writer.writerow([header for header, _ in _CSV_COLS])
        for row in rows:
            writer.writerow([EvaluationCritereController._csv_escape(str(row.get(key) or "")) for _, key in _CSV_COLS])
        content = output.getvalue().encode("utf-8")
        return Response(
            200,
            content,
            "text/csv; charset=utf-8",
            headers={
                "Content-Disposition": 'attachment; filename="evaluation_criteres.csv"',
                "Cache-Control": "no-store",
            },
        )
