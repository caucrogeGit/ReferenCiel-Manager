import csv
import io
from core.http.request import Request
from core.http.response import Response
from core.mvc.controller import BaseController
from core.mvc.view.pagination import Pagination
from mvc.models.item_coche_model import (
    get_item_coche_by_id, add_item_coche, update_item_coche, delete_item_coche, bulk_delete_item_coches,
    count_item_coches, find_item_coches_paginated, find_item_coches_for_export,
    get_item_checklist_choices, get_progression_seance_choices,
)
from mvc.forms.item_coche_form import ItemCocheForm
from core.security.session import get_flash, get_session_id


def _form_data_from_item_coche(record: dict) -> dict:
    """Convertit les colonnes SQL vers les noms de champs du formulaire."""
    return {
        "coche_eleve": record.get("CocheEleve"),
        "coche_professeur": record.get("CocheProfesseur"),
        "item_id": record.get("item_id"),
        "progression_seance_id": record.get("progression_seance_id"),
        "created_at": record.get("CreatedAt"),
        "updated_at": record.get("UpdatedAt"),
    }


def _item_coche_form_options():
    return {
        "item_id_choices": get_item_checklist_choices(),
        "progression_seance_id_choices": get_progression_seance_choices(),
    }


def _query_param(request, name, default=""):
    """Retourne le premier paramètre GET, au format parse_qs de Forge."""
    values = request.params.get(name, [default])
    return values[0] if values else default


def _is_hx_request(request):
    """Détecte une requête HTMX locale au CRUD généré."""
    return request.headers.get("HX-Request", "").lower() == "true"


_CSV_COLS = [('Coche eleve', 'CocheEleve'), ('Coche professeur', 'CocheProfesseur'), ('Item id', 'item_id_label'), ('Progression séance', 'progression_seance_id_label'), ('Created at', 'CreatedAt'), ('Updated at', 'UpdatedAt')]


class ItemCocheController(BaseController):

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
        if sort not in {"coche_eleve", "coche_professeur", "item_id", "progression_seance_id", "created_at", "updated_at", "id"}:
            sort = ""
        direction = _query_param(request, "direction", "desc")
        if direction not in ("asc", "desc"):
            direction = "asc"
        limit  = 20
        item_id_raw = _query_param(request, "item_id").strip()
        item_id_f = ""
        if item_id_raw:
            try:
                item_id_f = int(item_id_raw)
            except (TypeError, ValueError):
                item_id_f = ""
        progression_seance_id_raw = _query_param(request, "progression_seance_id").strip()
        progression_seance_id_f = ""
        if progression_seance_id_raw:
            try:
                progression_seance_id_f = int(progression_seance_id_raw)
            except (TypeError, ValueError):
                progression_seance_id_f = ""
        relation_filters = {}
        relation_filters["item_id"] = {"options": [{"id": value, "label": label} for value, label in get_item_checklist_choices()]}
        relation_filters["progression_seance_id"] = {"options": [{"id": value, "label": label} for value, label in get_progression_seance_choices()]}
        _filters = {}
        if item_id_f != "":
            _filters["item_id"] = item_id_f
        if progression_seance_id_f != "":
            _filters["progression_seance_id"] = progression_seance_id_f
        total    = count_item_coches(q or None, filters=_filters or None)
        pagination_state = Pagination(request, total, limit)
        limit = pagination_state.limit
        offset = pagination_state.offset
        empty_context = "search_filters" if q and _filters else ("search" if q else ("filters" if _filters else None))
        item_coches = find_item_coches_paginated(
            q=q or None, sort=sort or None, direction=direction,
            limit=limit, offset=offset, filters=_filters or None,
        )
        pagination = pagination_state.to_dict()
        pagination.update({
            "q": q, "sort": sort, "direction": direction,
            "filters": {"item_id": item_id_f, "progression_seance_id": progression_seance_id_f},
        })
        return {
                "item_coches": item_coches,
                "pagination": pagination,
                "empty_context": empty_context,
                "relation_filters": relation_filters,
                "flash": get_flash(get_session_id(request)),
            }

    @staticmethod
    def index(request: Request) -> Response:
        context = ItemCocheController._list_context(request)
        template = "app/item_coche/_results.html" if _is_hx_request(request) else "app/item_coche/index.html"
        return BaseController.render(template, context=context, request=request)

    @staticmethod
    def new(request: Request) -> Response:
        form = ItemCocheForm(**_item_coche_form_options())
        return BaseController.render("app/item_coche/form.html",
            context={
                "form": form,
                "action": "/item_coche/create",
                "titre": "Nouveau item_coche",
            },
            request=request)

    @staticmethod
    def create(request: Request) -> Response:
        form = ItemCocheForm.from_request(request, **_item_coche_form_options())
        if not form.is_valid():
            return BaseController.validation_error("app/item_coche/form.html",
                context={
                    "form": form,
                    "action": "/item_coche/create",
                    "titre": "Nouveau item_coche",
                },
                request=request)
        add_item_coche(form.cleaned_data)
        return BaseController.redirect_with_flash(request, "/item_coche", "ItemCoche créé.")

    @staticmethod
    def show(request: Request) -> Response:
        id = ItemCocheController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        item_coche = get_item_coche_by_id(id)
        if item_coche is None:
            return BaseController.not_found()
        return BaseController.render("app/item_coche/show.html",
            context={"item_coche": item_coche, "flash": get_flash(get_session_id(request))},
            request=request)

    @staticmethod
    def edit(request: Request) -> Response:
        id = ItemCocheController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        item_coche = get_item_coche_by_id(id)
        if item_coche is None:
            return BaseController.not_found()
        return BaseController.render("app/item_coche/form.html",
            context={
                "form": ItemCocheForm(_form_data_from_item_coche(item_coche), **_item_coche_form_options()),
                "action": f"/item_coche/update/{id}",
                "titre": "Modifier item_coche",
            },
            request=request)

    @staticmethod
    def update(request: Request) -> Response:
        id = ItemCocheController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        form = ItemCocheForm.from_request(request, **_item_coche_form_options())
        if not form.is_valid():
            return BaseController.validation_error("app/item_coche/form.html",
                context={
                    "form": form,
                    "action": f"/item_coche/update/{id}",
                    "titre": "Modifier item_coche",
                },
                request=request)
        update_item_coche(id, form.cleaned_data)
        return BaseController.redirect_with_flash(
            request, f"/item_coche/show/{id}", "ItemCoche mis à jour.")

    @staticmethod
    def destroy(request: Request) -> Response:
        id = ItemCocheController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        delete_item_coche(id)
        if _is_hx_request(request):
            context = ItemCocheController._list_context(request)
            return BaseController.render("app/item_coche/_results.html", context=context, request=request)
        return BaseController.redirect_with_flash(request, "/item_coche", "ItemCoche supprimé.")


    @staticmethod
    def bulk_delete(request: Request) -> Response:
        ids = ItemCocheController._parse_bulk_ids(request)
        if not ids:
            return BaseController.redirect_with_flash(request, "/item_coche", "Aucun élément sélectionné.")
        return BaseController.render("app/item_coche/bulk_delete_confirm.html",
            context={"ids": ids, "count": len(ids), "flash": get_flash(get_session_id(request))},
            request=request)

    @staticmethod
    def bulk_delete_confirm(request: Request) -> Response:
        ids = ItemCocheController._parse_bulk_ids(request)
        if not ids:
            return BaseController.redirect_with_flash(request, "/item_coche", "Aucun élément sélectionné.")
        bulk_delete_item_coches(ids)
        count = len(ids)
        return BaseController.redirect_with_flash(
            request, "/item_coche",
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
        if sort not in {"coche_eleve", "coche_professeur", "item_id", "progression_seance_id", "created_at", "updated_at", "id"}:
            sort = ""
        direction = _query_param(request, "direction", "desc")
        if direction not in ("asc", "desc"):
            direction = "asc"
        item_id_raw = _query_param(request, "item_id").strip()
        item_id_f = ""
        if item_id_raw:
            try:
                item_id_f = int(item_id_raw)
            except (TypeError, ValueError):
                item_id_f = ""
        progression_seance_id_raw = _query_param(request, "progression_seance_id").strip()
        progression_seance_id_f = ""
        if progression_seance_id_raw:
            try:
                progression_seance_id_f = int(progression_seance_id_raw)
            except (TypeError, ValueError):
                progression_seance_id_f = ""
        _filters = {}
        if item_id_f != "":
            _filters["item_id"] = item_id_f
        if progression_seance_id_f != "":
            _filters["progression_seance_id"] = progression_seance_id_f
        rows = find_item_coches_for_export(q=q or None, sort=sort or None, direction=direction, filters=_filters or None)
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_ALL)
        writer.writerow([header for header, _ in _CSV_COLS])
        for row in rows:
            writer.writerow([ItemCocheController._csv_escape(str(row.get(key) or "")) for _, key in _CSV_COLS])
        content = output.getvalue().encode("utf-8")
        return Response(
            200,
            content,
            "text/csv; charset=utf-8",
            headers={
                "Content-Disposition": 'attachment; filename="item_coches.csv"',
                "Cache-Control": "no-store",
            },
        )
