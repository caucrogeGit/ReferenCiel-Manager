import csv
import io
from core.http.request import Request
from core.http.response import Response
from core.mvc.controller import BaseController
from core.mvc.view.pagination import Pagination
from mvc.models.item_checklist_model import (
    get_item_checklist_by_id, add_item_checklist, update_item_checklist, delete_item_checklist, bulk_delete_item_checklists,
    count_item_checklists, find_item_checklists_paginated, find_item_checklists_for_export,
    get_section_checklist_choices,
)
from mvc.forms.item_checklist_form import ItemChecklistForm
from core.security.session import get_flash, get_session_id


def _form_data_from_item_checklist(record: dict) -> dict:
    """Convertit les colonnes SQL vers les noms de champs du formulaire."""
    return {
        "libelle": record.get("Libelle"),
        "section_id": record.get("section_id"),
        "created_at": record.get("CreatedAt"),
        "updated_at": record.get("UpdatedAt"),
    }


def _item_checklist_form_options():
    return {
        "section_id_choices": get_section_checklist_choices(),
    }


def _query_param(request, name, default=""):
    """Retourne le premier paramètre GET, au format parse_qs de Forge."""
    values = request.params.get(name, [default])
    return values[0] if values else default


def _is_hx_request(request):
    """Détecte une requête HTMX locale au CRUD généré."""
    return request.headers.get("HX-Request", "").lower() == "true"


_CSV_COLS = [('Libelle', 'Libelle'), ('Section id', 'section_id_label'), ('Created at', 'CreatedAt'), ('Updated at', 'UpdatedAt')]


class ItemChecklistController(BaseController):

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
        if sort not in {"libelle", "section_id", "created_at", "updated_at", "id"}:
            sort = ""
        direction = _query_param(request, "direction", "desc")
        if direction not in ("asc", "desc"):
            direction = "asc"
        limit  = 20
        section_id_raw = _query_param(request, "section_id").strip()
        section_id_f = ""
        if section_id_raw:
            try:
                section_id_f = int(section_id_raw)
            except (TypeError, ValueError):
                section_id_f = ""
        relation_filters = {}
        relation_filters["section_id"] = {"options": [{"id": value, "label": label} for value, label in get_section_checklist_choices()]}
        _filters = {}
        if section_id_f != "":
            _filters["section_id"] = section_id_f
        total    = count_item_checklists(q or None, filters=_filters or None)
        pagination_state = Pagination(request, total, limit)
        limit = pagination_state.limit
        offset = pagination_state.offset
        empty_context = "search_filters" if q and _filters else ("search" if q else ("filters" if _filters else None))
        item_checklists = find_item_checklists_paginated(
            q=q or None, sort=sort or None, direction=direction,
            limit=limit, offset=offset, filters=_filters or None,
        )
        pagination = pagination_state.to_dict()
        pagination.update({
            "q": q, "sort": sort, "direction": direction,
            "filters": {"section_id": section_id_f},
        })
        return {
                "item_checklists": item_checklists,
                "pagination": pagination,
                "empty_context": empty_context,
                "relation_filters": relation_filters,
                "flash": get_flash(get_session_id(request)),
            }

    @staticmethod
    def index(request: Request) -> Response:
        context = ItemChecklistController._list_context(request)
        template = "item_checklist/_results.html" if _is_hx_request(request) else "item_checklist/index.html"
        return BaseController.render(template, context=context, request=request)

    @staticmethod
    def new(request: Request) -> Response:
        form = ItemChecklistForm(**_item_checklist_form_options())
        return BaseController.render("item_checklist/form.html",
            context={
                "form": form,
                "action": "/item_checklist/create",
                "titre": "Nouveau item_checklist",
            },
            request=request)

    @staticmethod
    def create(request: Request) -> Response:
        form = ItemChecklistForm.from_request(request, **_item_checklist_form_options())
        if not form.is_valid():
            return BaseController.validation_error("item_checklist/form.html",
                context={
                    "form": form,
                    "action": "/item_checklist/create",
                    "titre": "Nouveau item_checklist",
                },
                request=request)
        add_item_checklist(form.cleaned_data)
        return BaseController.redirect_with_flash(request, "/item_checklist", "ItemChecklist créé.")

    @staticmethod
    def show(request: Request) -> Response:
        id = ItemChecklistController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        item_checklist = get_item_checklist_by_id(id)
        if item_checklist is None:
            return BaseController.not_found()
        return BaseController.render("item_checklist/show.html",
            context={"item_checklist": item_checklist, "flash": get_flash(get_session_id(request))},
            request=request)

    @staticmethod
    def edit(request: Request) -> Response:
        id = ItemChecklistController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        item_checklist = get_item_checklist_by_id(id)
        if item_checklist is None:
            return BaseController.not_found()
        return BaseController.render("item_checklist/form.html",
            context={
                "form": ItemChecklistForm(_form_data_from_item_checklist(item_checklist), **_item_checklist_form_options()),
                "action": f"/item_checklist/update/{id}",
                "titre": "Modifier item_checklist",
            },
            request=request)

    @staticmethod
    def update(request: Request) -> Response:
        id = ItemChecklistController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        form = ItemChecklistForm.from_request(request, **_item_checklist_form_options())
        if not form.is_valid():
            return BaseController.validation_error("item_checklist/form.html",
                context={
                    "form": form,
                    "action": f"/item_checklist/update/{id}",
                    "titre": "Modifier item_checklist",
                },
                request=request)
        update_item_checklist(id, form.cleaned_data)
        return BaseController.redirect_with_flash(
            request, f"/item_checklist/show/{id}", "ItemChecklist mis à jour.")

    @staticmethod
    def destroy(request: Request) -> Response:
        id = ItemChecklistController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        delete_item_checklist(id)
        if _is_hx_request(request):
            context = ItemChecklistController._list_context(request)
            return BaseController.render("item_checklist/_results.html", context=context, request=request)
        return BaseController.redirect_with_flash(request, "/item_checklist", "ItemChecklist supprimé.")


    @staticmethod
    def bulk_delete(request: Request) -> Response:
        ids = ItemChecklistController._parse_bulk_ids(request)
        if not ids:
            return BaseController.redirect_with_flash(request, "/item_checklist", "Aucun élément sélectionné.")
        return BaseController.render("item_checklist/bulk_delete_confirm.html",
            context={"ids": ids, "count": len(ids), "flash": get_flash(get_session_id(request))},
            request=request)

    @staticmethod
    def bulk_delete_confirm(request: Request) -> Response:
        ids = ItemChecklistController._parse_bulk_ids(request)
        if not ids:
            return BaseController.redirect_with_flash(request, "/item_checklist", "Aucun élément sélectionné.")
        bulk_delete_item_checklists(ids)
        count = len(ids)
        return BaseController.redirect_with_flash(
            request, "/item_checklist",
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
        if sort not in {"libelle", "section_id", "created_at", "updated_at", "id"}:
            sort = ""
        direction = _query_param(request, "direction", "desc")
        if direction not in ("asc", "desc"):
            direction = "asc"
        section_id_raw = _query_param(request, "section_id").strip()
        section_id_f = ""
        if section_id_raw:
            try:
                section_id_f = int(section_id_raw)
            except (TypeError, ValueError):
                section_id_f = ""
        _filters = {}
        if section_id_f != "":
            _filters["section_id"] = section_id_f
        rows = find_item_checklists_for_export(q=q or None, sort=sort or None, direction=direction, filters=_filters or None)
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_ALL)
        writer.writerow([header for header, _ in _CSV_COLS])
        for row in rows:
            writer.writerow([ItemChecklistController._csv_escape(str(row.get(key) or "")) for _, key in _CSV_COLS])
        content = output.getvalue().encode("utf-8")
        return Response(
            200,
            content,
            "text/csv; charset=utf-8",
            headers={
                "Content-Disposition": 'attachment; filename="item_checklists.csv"',
                "Cache-Control": "no-store",
            },
        )
