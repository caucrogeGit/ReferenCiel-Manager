import csv
import io
from core.http.request import Request
from core.http.response import Response
from core.mvc.controller import BaseController
from core.mvc.view.pagination import Pagination
from mvc.models.progression_palier_model import (
    get_progression_palier_by_id, add_progression_palier, update_progression_palier, delete_progression_palier, bulk_delete_progression_paliers,
    count_progression_paliers, find_progression_paliers_paginated, find_progression_paliers_for_export,
    get_progression_eleve_choices, get_palier_choices,
)
from mvc.forms.progression_palier_form import ProgressionPalierForm
from core.security.session import get_flash, get_session_id


def _form_data_from_progression_palier(record: dict) -> dict:
    """Convertit les colonnes SQL vers les noms de champs du formulaire."""
    return {
        "statut": record.get("Statut"),
        "progression_eleve_id": record.get("progression_eleve_id"),
        "palier_id": record.get("palier_id"),
        "created_at": record.get("CreatedAt"),
        "updated_at": record.get("UpdatedAt"),
    }


def _progression_palier_form_options():
    return {
        "progression_eleve_id_choices": get_progression_eleve_choices(),
        "palier_id_choices": get_palier_choices(),
    }


def _query_param(request, name, default=""):
    """Retourne le premier paramètre GET, au format parse_qs de Forge."""
    values = request.params.get(name, [default])
    return values[0] if values else default


def _is_hx_request(request):
    """Détecte une requête HTMX locale au CRUD généré."""
    return request.headers.get("HX-Request", "").lower() == "true"


_CSV_COLS = [('Statut', 'Statut'), ('Progression eleve id', 'progression_eleve_id_label'), ('Palier id', 'palier_id_label'), ('Created at', 'CreatedAt'), ('Updated at', 'UpdatedAt')]


class ProgressionPalierController(BaseController):

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
        if sort not in {"statut", "progression_eleve_id", "palier_id", "created_at", "updated_at", "id"}:
            sort = ""
        direction = _query_param(request, "direction", "desc")
        if direction not in ("asc", "desc"):
            direction = "asc"
        limit  = 20
        progression_eleve_id_raw = _query_param(request, "progression_eleve_id").strip()
        progression_eleve_id_f = ""
        if progression_eleve_id_raw:
            try:
                progression_eleve_id_f = int(progression_eleve_id_raw)
            except (TypeError, ValueError):
                progression_eleve_id_f = ""
        palier_id_raw = _query_param(request, "palier_id").strip()
        palier_id_f = ""
        if palier_id_raw:
            try:
                palier_id_f = int(palier_id_raw)
            except (TypeError, ValueError):
                palier_id_f = ""
        relation_filters = {}
        relation_filters["progression_eleve_id"] = {"options": [{"id": value, "label": label} for value, label in get_progression_eleve_choices()]}
        relation_filters["palier_id"] = {"options": [{"id": value, "label": label} for value, label in get_palier_choices()]}
        _filters = {}
        if progression_eleve_id_f != "":
            _filters["progression_eleve_id"] = progression_eleve_id_f
        if palier_id_f != "":
            _filters["palier_id"] = palier_id_f
        total    = count_progression_paliers(q or None, filters=_filters or None)
        pagination_state = Pagination(request, total, limit)
        limit = pagination_state.limit
        offset = pagination_state.offset
        empty_context = "search_filters" if q and _filters else ("search" if q else ("filters" if _filters else None))
        progression_paliers = find_progression_paliers_paginated(
            q=q or None, sort=sort or None, direction=direction,
            limit=limit, offset=offset, filters=_filters or None,
        )
        pagination = pagination_state.to_dict()
        pagination.update({
            "q": q, "sort": sort, "direction": direction,
            "filters": {"progression_eleve_id": progression_eleve_id_f, "palier_id": palier_id_f},
        })
        return {
                "progression_paliers": progression_paliers,
                "pagination": pagination,
                "empty_context": empty_context,
                "relation_filters": relation_filters,
                "flash": get_flash(get_session_id(request)),
            }

    @staticmethod
    def index(request: Request) -> Response:
        context = ProgressionPalierController._list_context(request)
        template = "app/progression_palier/_results.html" if _is_hx_request(request) else "app/progression_palier/index.html"
        return BaseController.render(template, context=context, request=request)

    @staticmethod
    def new(request: Request) -> Response:
        form = ProgressionPalierForm(**_progression_palier_form_options())
        return BaseController.render("app/progression_palier/form.html",
            context={
                "form": form,
                "action": "/progression_palier/create",
                "titre": "Nouveau progression_palier",
            },
            request=request)

    @staticmethod
    def create(request: Request) -> Response:
        form = ProgressionPalierForm.from_request(request, **_progression_palier_form_options())
        if not form.is_valid():
            return BaseController.validation_error("app/progression_palier/form.html",
                context={
                    "form": form,
                    "action": "/progression_palier/create",
                    "titre": "Nouveau progression_palier",
                },
                request=request)
        add_progression_palier(form.cleaned_data)
        return BaseController.redirect_with_flash(request, "/progression_palier", "ProgressionPalier créé.")

    @staticmethod
    def show(request: Request) -> Response:
        id = ProgressionPalierController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        progression_palier = get_progression_palier_by_id(id)
        if progression_palier is None:
            return BaseController.not_found()
        return BaseController.render("app/progression_palier/show.html",
            context={"progression_palier": progression_palier, "flash": get_flash(get_session_id(request))},
            request=request)

    @staticmethod
    def edit(request: Request) -> Response:
        id = ProgressionPalierController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        progression_palier = get_progression_palier_by_id(id)
        if progression_palier is None:
            return BaseController.not_found()
        return BaseController.render("app/progression_palier/form.html",
            context={
                "form": ProgressionPalierForm(_form_data_from_progression_palier(progression_palier), **_progression_palier_form_options()),
                "action": f"/progression_palier/update/{id}",
                "titre": "Modifier progression_palier",
            },
            request=request)

    @staticmethod
    def update(request: Request) -> Response:
        id = ProgressionPalierController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        form = ProgressionPalierForm.from_request(request, **_progression_palier_form_options())
        if not form.is_valid():
            return BaseController.validation_error("app/progression_palier/form.html",
                context={
                    "form": form,
                    "action": f"/progression_palier/update/{id}",
                    "titre": "Modifier progression_palier",
                },
                request=request)
        update_progression_palier(id, form.cleaned_data)
        return BaseController.redirect_with_flash(
            request, f"/progression_palier/show/{id}", "ProgressionPalier mis à jour.")

    @staticmethod
    def destroy(request: Request) -> Response:
        id = ProgressionPalierController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        delete_progression_palier(id)
        if _is_hx_request(request):
            context = ProgressionPalierController._list_context(request)
            return BaseController.render("app/progression_palier/_results.html", context=context, request=request)
        return BaseController.redirect_with_flash(request, "/progression_palier", "ProgressionPalier supprimé.")


    @staticmethod
    def bulk_delete(request: Request) -> Response:
        ids = ProgressionPalierController._parse_bulk_ids(request)
        if not ids:
            return BaseController.redirect_with_flash(request, "/progression_palier", "Aucun élément sélectionné.")
        return BaseController.render("app/progression_palier/bulk_delete_confirm.html",
            context={"ids": ids, "count": len(ids), "flash": get_flash(get_session_id(request))},
            request=request)

    @staticmethod
    def bulk_delete_confirm(request: Request) -> Response:
        ids = ProgressionPalierController._parse_bulk_ids(request)
        if not ids:
            return BaseController.redirect_with_flash(request, "/progression_palier", "Aucun élément sélectionné.")
        bulk_delete_progression_paliers(ids)
        count = len(ids)
        return BaseController.redirect_with_flash(
            request, "/progression_palier",
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
        if sort not in {"statut", "progression_eleve_id", "palier_id", "created_at", "updated_at", "id"}:
            sort = ""
        direction = _query_param(request, "direction", "desc")
        if direction not in ("asc", "desc"):
            direction = "asc"
        progression_eleve_id_raw = _query_param(request, "progression_eleve_id").strip()
        progression_eleve_id_f = ""
        if progression_eleve_id_raw:
            try:
                progression_eleve_id_f = int(progression_eleve_id_raw)
            except (TypeError, ValueError):
                progression_eleve_id_f = ""
        palier_id_raw = _query_param(request, "palier_id").strip()
        palier_id_f = ""
        if palier_id_raw:
            try:
                palier_id_f = int(palier_id_raw)
            except (TypeError, ValueError):
                palier_id_f = ""
        _filters = {}
        if progression_eleve_id_f != "":
            _filters["progression_eleve_id"] = progression_eleve_id_f
        if palier_id_f != "":
            _filters["palier_id"] = palier_id_f
        rows = find_progression_paliers_for_export(q=q or None, sort=sort or None, direction=direction, filters=_filters or None)
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_ALL)
        writer.writerow([header for header, _ in _CSV_COLS])
        for row in rows:
            writer.writerow([ProgressionPalierController._csv_escape(str(row.get(key) or "")) for _, key in _CSV_COLS])
        content = output.getvalue().encode("utf-8")
        return Response(
            200,
            content,
            "text/csv; charset=utf-8",
            headers={
                "Content-Disposition": 'attachment; filename="progression_paliers.csv"',
                "Cache-Control": "no-store",
            },
        )
