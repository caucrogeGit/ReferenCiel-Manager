import csv
import io
from core.http.request import Request
from core.http.response import Response
from core.mvc.controller import BaseController
from core.mvc.view.pagination import Pagination
from mvc.models.section_checklist_model import (
    get_section_checklist_by_id, add_section_checklist, update_section_checklist, delete_section_checklist, bulk_delete_section_checklists,
    count_section_checklists, find_section_checklists_paginated, find_section_checklists_for_export,
    get_checklist_choices,
)
from mvc.forms.section_checklist_form import SectionChecklistForm
from core.security.session import get_flash, get_session_id


def _form_data_from_section_checklist(record: dict) -> dict:
    """Convertit les colonnes SQL vers les noms de champs du formulaire."""
    return {
        "numero": record.get("Numero"),
        "titre": record.get("Titre"),
        "checklist_id": record.get("checklist_id"),
        "created_at": record.get("CreatedAt"),
        "updated_at": record.get("UpdatedAt"),
    }


def _section_checklist_form_options():
    return {
        "checklist_id_choices": get_checklist_choices(),
    }


def _query_param(request, name, default=""):
    """Retourne le premier paramètre GET, au format parse_qs de Forge."""
    values = request.params.get(name, [default])
    return values[0] if values else default


def _is_hx_request(request):
    """Détecte une requête HTMX locale au CRUD généré."""
    return request.headers.get("HX-Request", "").lower() == "true"


_CSV_COLS = [('Numero', 'Numero'), ('Titre', 'Titre'), ('Checklist id', 'checklist_id_label'), ('Created at', 'CreatedAt'), ('Updated at', 'UpdatedAt')]


class SectionChecklistController(BaseController):

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
        if sort not in {"numero", "titre", "checklist_id", "created_at", "updated_at", "id"}:
            sort = ""
        direction = _query_param(request, "direction", "desc")
        if direction not in ("asc", "desc"):
            direction = "asc"
        limit  = 20
        checklist_id_raw = _query_param(request, "checklist_id").strip()
        checklist_id_f = ""
        if checklist_id_raw:
            try:
                checklist_id_f = int(checklist_id_raw)
            except (TypeError, ValueError):
                checklist_id_f = ""
        relation_filters = {}
        relation_filters["checklist_id"] = {"options": [{"id": value, "label": label} for value, label in get_checklist_choices()]}
        _filters = {}
        if checklist_id_f != "":
            _filters["checklist_id"] = checklist_id_f
        total    = count_section_checklists(q or None, filters=_filters or None)
        pagination_state = Pagination(request, total, limit)
        limit = pagination_state.limit
        offset = pagination_state.offset
        empty_context = "search_filters" if q and _filters else ("search" if q else ("filters" if _filters else None))
        section_checklists = find_section_checklists_paginated(
            q=q or None, sort=sort or None, direction=direction,
            limit=limit, offset=offset, filters=_filters or None,
        )
        pagination = pagination_state.to_dict()
        pagination.update({
            "q": q, "sort": sort, "direction": direction,
            "filters": {"checklist_id": checklist_id_f},
        })
        return {
                "section_checklists": section_checklists,
                "pagination": pagination,
                "empty_context": empty_context,
                "relation_filters": relation_filters,
                "flash": get_flash(get_session_id(request)),
            }

    @staticmethod
    def index(request: Request) -> Response:
        context = SectionChecklistController._list_context(request)
        template = "app/section_checklist/_results.html" if _is_hx_request(request) else "app/section_checklist/index.html"
        return BaseController.render(template, context=context, request=request)

    @staticmethod
    def new(request: Request) -> Response:
        form = SectionChecklistForm(**_section_checklist_form_options())
        return BaseController.render("app/section_checklist/form.html",
            context={
                "form": form,
                "action": "/section_checklist/create",
                "titre": "Nouveau section_checklist",
            },
            request=request)

    @staticmethod
    def create(request: Request) -> Response:
        form = SectionChecklistForm.from_request(request, **_section_checklist_form_options())
        if not form.is_valid():
            return BaseController.validation_error("app/section_checklist/form.html",
                context={
                    "form": form,
                    "action": "/section_checklist/create",
                    "titre": "Nouveau section_checklist",
                },
                request=request)
        add_section_checklist(form.cleaned_data)
        return BaseController.redirect_with_flash(request, "/section_checklist", "SectionChecklist créé.")

    @staticmethod
    def show(request: Request) -> Response:
        id = SectionChecklistController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        section_checklist = get_section_checklist_by_id(id)
        if section_checklist is None:
            return BaseController.not_found()
        return BaseController.render("app/section_checklist/show.html",
            context={"section_checklist": section_checklist, "flash": get_flash(get_session_id(request))},
            request=request)

    @staticmethod
    def edit(request: Request) -> Response:
        id = SectionChecklistController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        section_checklist = get_section_checklist_by_id(id)
        if section_checklist is None:
            return BaseController.not_found()
        return BaseController.render("app/section_checklist/form.html",
            context={
                "form": SectionChecklistForm(_form_data_from_section_checklist(section_checklist), **_section_checklist_form_options()),
                "action": f"/section_checklist/update/{id}",
                "titre": "Modifier section_checklist",
            },
            request=request)

    @staticmethod
    def update(request: Request) -> Response:
        id = SectionChecklistController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        form = SectionChecklistForm.from_request(request, **_section_checklist_form_options())
        if not form.is_valid():
            return BaseController.validation_error("app/section_checklist/form.html",
                context={
                    "form": form,
                    "action": f"/section_checklist/update/{id}",
                    "titre": "Modifier section_checklist",
                },
                request=request)
        update_section_checklist(id, form.cleaned_data)
        return BaseController.redirect_with_flash(
            request, f"/section_checklist/show/{id}", "SectionChecklist mis à jour.")

    @staticmethod
    def destroy(request: Request) -> Response:
        id = SectionChecklistController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        delete_section_checklist(id)
        if _is_hx_request(request):
            context = SectionChecklistController._list_context(request)
            return BaseController.render("app/section_checklist/_results.html", context=context, request=request)
        return BaseController.redirect_with_flash(request, "/section_checklist", "SectionChecklist supprimé.")


    @staticmethod
    def bulk_delete(request: Request) -> Response:
        ids = SectionChecklistController._parse_bulk_ids(request)
        if not ids:
            return BaseController.redirect_with_flash(request, "/section_checklist", "Aucun élément sélectionné.")
        return BaseController.render("app/section_checklist/bulk_delete_confirm.html",
            context={"ids": ids, "count": len(ids), "flash": get_flash(get_session_id(request))},
            request=request)

    @staticmethod
    def bulk_delete_confirm(request: Request) -> Response:
        ids = SectionChecklistController._parse_bulk_ids(request)
        if not ids:
            return BaseController.redirect_with_flash(request, "/section_checklist", "Aucun élément sélectionné.")
        bulk_delete_section_checklists(ids)
        count = len(ids)
        return BaseController.redirect_with_flash(
            request, "/section_checklist",
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
        if sort not in {"numero", "titre", "checklist_id", "created_at", "updated_at", "id"}:
            sort = ""
        direction = _query_param(request, "direction", "desc")
        if direction not in ("asc", "desc"):
            direction = "asc"
        checklist_id_raw = _query_param(request, "checklist_id").strip()
        checklist_id_f = ""
        if checklist_id_raw:
            try:
                checklist_id_f = int(checklist_id_raw)
            except (TypeError, ValueError):
                checklist_id_f = ""
        _filters = {}
        if checklist_id_f != "":
            _filters["checklist_id"] = checklist_id_f
        rows = find_section_checklists_for_export(q=q or None, sort=sort or None, direction=direction, filters=_filters or None)
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_ALL)
        writer.writerow([header for header, _ in _CSV_COLS])
        for row in rows:
            writer.writerow([SectionChecklistController._csv_escape(str(row.get(key) or "")) for _, key in _CSV_COLS])
        content = output.getvalue().encode("utf-8")
        return Response(
            200,
            content,
            "text/csv; charset=utf-8",
            headers={
                "Content-Disposition": 'attachment; filename="section_checklists.csv"',
                "Cache-Control": "no-store",
            },
        )
