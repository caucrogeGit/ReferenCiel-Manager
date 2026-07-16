import csv
import io
from core.http.request import Request
from core.http.response import Response
from core.mvc.controller import BaseController
from core.mvc.view.pagination import Pagination
from mvc.models.progression_seance_model import (
    get_progression_seance_by_id, add_progression_seance, update_progression_seance, delete_progression_seance, bulk_delete_progression_seances,
    count_progression_seances, find_progression_seances_paginated, find_progression_seances_for_export,
    get_progression_sequence_choices, get_seance_choices,
)
from mvc.forms.progression_seance_form import ProgressionSeanceForm
from core.security.session import get_flash, get_session_id


def _form_data_from_progression_seance(record: dict) -> dict:
    """Convertit les colonnes SQL vers les noms de champs du formulaire."""
    return {
        "statut": record.get("Statut"),
        "progression_sequence_id": record.get("progression_sequence_id"),
        "seance_id": record.get("seance_id"),
        "created_at": record.get("CreatedAt"),
        "updated_at": record.get("UpdatedAt"),
    }


def _progression_seance_form_options():
    return {
        "progression_sequence_id_choices": get_progression_sequence_choices(),
        "seance_id_choices": get_seance_choices(),
    }


def _query_param(request, name, default=""):
    """Retourne le premier paramètre GET, au format parse_qs de Forge."""
    values = request.params.get(name, [default])
    return values[0] if values else default


def _is_hx_request(request):
    """Détecte une requête HTMX locale au CRUD généré."""
    return request.headers.get("HX-Request", "").lower() == "true"


_CSV_COLS = [('Statut', 'Statut'), ('Progression eleve id', 'progression_sequence_id_label'), ('Séance', 'seance_id_label'), ('Created at', 'CreatedAt'), ('Updated at', 'UpdatedAt')]


class ProgressionSeanceController(BaseController):

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
        if sort not in {"statut", "progression_sequence_id", "seance_id", "created_at", "updated_at", "id"}:
            sort = ""
        direction = _query_param(request, "direction", "desc")
        if direction not in ("asc", "desc"):
            direction = "asc"
        limit  = 20
        progression_sequence_id_raw = _query_param(request, "progression_sequence_id").strip()
        progression_sequence_id_f = ""
        if progression_sequence_id_raw:
            try:
                progression_sequence_id_f = int(progression_sequence_id_raw)
            except (TypeError, ValueError):
                progression_sequence_id_f = ""
        seance_id_raw = _query_param(request, "seance_id").strip()
        seance_id_f = ""
        if seance_id_raw:
            try:
                seance_id_f = int(seance_id_raw)
            except (TypeError, ValueError):
                seance_id_f = ""
        relation_filters = {}
        relation_filters["progression_sequence_id"] = {"options": [{"id": value, "label": label} for value, label in get_progression_sequence_choices()]}
        relation_filters["seance_id"] = {"options": [{"id": value, "label": label} for value, label in get_seance_choices()]}
        _filters = {}
        if progression_sequence_id_f != "":
            _filters["progression_sequence_id"] = progression_sequence_id_f
        if seance_id_f != "":
            _filters["seance_id"] = seance_id_f
        total    = count_progression_seances(q or None, filters=_filters or None)
        pagination_state = Pagination(request, total, limit)
        limit = pagination_state.limit
        offset = pagination_state.offset
        empty_context = "search_filters" if q and _filters else ("search" if q else ("filters" if _filters else None))
        progression_seances = find_progression_seances_paginated(
            q=q or None, sort=sort or None, direction=direction,
            limit=limit, offset=offset, filters=_filters or None,
        )
        pagination = pagination_state.to_dict()
        pagination.update({
            "q": q, "sort": sort, "direction": direction,
            "filters": {"progression_sequence_id": progression_sequence_id_f, "seance_id": seance_id_f},
        })
        return {
                "progression_seances": progression_seances,
                "pagination": pagination,
                "empty_context": empty_context,
                "relation_filters": relation_filters,
                "flash": get_flash(get_session_id(request)),
            }

    @staticmethod
    def index(request: Request) -> Response:
        context = ProgressionSeanceController._list_context(request)
        template = "app/progression_seance/_results.html" if _is_hx_request(request) else "app/progression_seance/index.html"
        return BaseController.render(template, context=context, request=request)

    @staticmethod
    def new(request: Request) -> Response:
        form = ProgressionSeanceForm(**_progression_seance_form_options())
        return BaseController.render("app/progression_seance/form.html",
            context={
                "form": form,
                "action": "/progression_seance/create",
                "titre": "Nouvelle progression de séance",
            },
            request=request)

    @staticmethod
    def create(request: Request) -> Response:
        form = ProgressionSeanceForm.from_request(request, **_progression_seance_form_options())
        if not form.is_valid():
            return BaseController.validation_error("app/progression_seance/form.html",
                context={
                    "form": form,
                    "action": "/progression_seance/create",
                    "titre": "Nouvelle progression de séance",
                },
                request=request)
        add_progression_seance(form.cleaned_data)
        return BaseController.redirect_with_flash(request, "/progression_seance", "Progression de séance créée.")

    @staticmethod
    def show(request: Request) -> Response:
        id = ProgressionSeanceController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        progression_seance = get_progression_seance_by_id(id)
        if progression_seance is None:
            return BaseController.not_found()
        return BaseController.render("app/progression_seance/show.html",
            context={"progression_seance": progression_seance, "flash": get_flash(get_session_id(request))},
            request=request)

    @staticmethod
    def edit(request: Request) -> Response:
        id = ProgressionSeanceController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        progression_seance = get_progression_seance_by_id(id)
        if progression_seance is None:
            return BaseController.not_found()
        return BaseController.render("app/progression_seance/form.html",
            context={
                "form": ProgressionSeanceForm(_form_data_from_progression_seance(progression_seance), **_progression_seance_form_options()),
                "action": f"/progression_seance/update/{id}",
                "titre": "Modifier la progression de séance",
            },
            request=request)

    @staticmethod
    def update(request: Request) -> Response:
        id = ProgressionSeanceController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        form = ProgressionSeanceForm.from_request(request, **_progression_seance_form_options())
        if not form.is_valid():
            return BaseController.validation_error("app/progression_seance/form.html",
                context={
                    "form": form,
                    "action": f"/progression_seance/update/{id}",
                    "titre": "Modifier la progression de séance",
                },
                request=request)
        update_progression_seance(id, form.cleaned_data)
        return BaseController.redirect_with_flash(
            request, f"/progression_seance/show/{id}", "Progression de séance mise à jour.")

    @staticmethod
    def destroy(request: Request) -> Response:
        id = ProgressionSeanceController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        delete_progression_seance(id)
        if _is_hx_request(request):
            context = ProgressionSeanceController._list_context(request)
            return BaseController.render("app/progression_seance/_results.html", context=context, request=request)
        return BaseController.redirect_with_flash(request, "/progression_seance", "Progression de séance supprimée.")


    @staticmethod
    def bulk_delete(request: Request) -> Response:
        ids = ProgressionSeanceController._parse_bulk_ids(request)
        if not ids:
            return BaseController.redirect_with_flash(request, "/progression_seance", "Aucun élément sélectionné.")
        return BaseController.render("app/progression_seance/bulk_delete_confirm.html",
            context={"ids": ids, "count": len(ids), "flash": get_flash(get_session_id(request))},
            request=request)

    @staticmethod
    def bulk_delete_confirm(request: Request) -> Response:
        ids = ProgressionSeanceController._parse_bulk_ids(request)
        if not ids:
            return BaseController.redirect_with_flash(request, "/progression_seance", "Aucun élément sélectionné.")
        bulk_delete_progression_seances(ids)
        count = len(ids)
        return BaseController.redirect_with_flash(
            request, "/progression_seance",
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
        if sort not in {"statut", "progression_sequence_id", "seance_id", "created_at", "updated_at", "id"}:
            sort = ""
        direction = _query_param(request, "direction", "desc")
        if direction not in ("asc", "desc"):
            direction = "asc"
        progression_sequence_id_raw = _query_param(request, "progression_sequence_id").strip()
        progression_sequence_id_f = ""
        if progression_sequence_id_raw:
            try:
                progression_sequence_id_f = int(progression_sequence_id_raw)
            except (TypeError, ValueError):
                progression_sequence_id_f = ""
        seance_id_raw = _query_param(request, "seance_id").strip()
        seance_id_f = ""
        if seance_id_raw:
            try:
                seance_id_f = int(seance_id_raw)
            except (TypeError, ValueError):
                seance_id_f = ""
        _filters = {}
        if progression_sequence_id_f != "":
            _filters["progression_sequence_id"] = progression_sequence_id_f
        if seance_id_f != "":
            _filters["seance_id"] = seance_id_f
        rows = find_progression_seances_for_export(q=q or None, sort=sort or None, direction=direction, filters=_filters or None)
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_ALL)
        writer.writerow([header for header, _ in _CSV_COLS])
        for row in rows:
            writer.writerow([ProgressionSeanceController._csv_escape(str(row.get(key) or "")) for _, key in _CSV_COLS])
        content = output.getvalue().encode("utf-8")
        return Response(
            200,
            content,
            "text/csv; charset=utf-8",
            headers={
                "Content-Disposition": 'attachment; filename="progression_seances.csv"',
                "Cache-Control": "no-store",
            },
        )
