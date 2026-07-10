import csv
import io
from core.http.request import Request
from core.http.response import Response
from core.mvc.controller import BaseController
from core.mvc.view.pagination import Pagination
from mvc.models.parcours_model import (
    get_parcours_by_id, add_parcours, update_parcours, delete_parcours, bulk_delete_parcourss,
    count_parcourss, find_parcourss_paginated, find_parcourss_for_export,
    get_version_starter_choices,
)
from mvc.forms.parcours_form import ParcoursForm
from core.security.session import get_flash, get_session_id


def _form_data_from_parcours(record: dict) -> dict:
    """Convertit les colonnes SQL vers les noms de champs du formulaire."""
    return {
        "titre": record.get("Titre"),
        "version_starter_id": record.get("version_starter_id"),
        "created_at": record.get("CreatedAt"),
        "updated_at": record.get("UpdatedAt"),
    }


def _parcours_form_options():
    return {
        "version_starter_id_choices": get_version_starter_choices(),
    }


def _query_param(request, name, default=""):
    """Retourne le premier paramètre GET, au format parse_qs de Forge."""
    values = request.params.get(name, [default])
    return values[0] if values else default


def _is_hx_request(request):
    """Détecte une requête HTMX locale au CRUD généré."""
    return request.headers.get("HX-Request", "").lower() == "true"


_CSV_COLS = [('Titre', 'Titre'), ('Version starter id', 'version_starter_id_label'), ('Created at', 'CreatedAt'), ('Updated at', 'UpdatedAt')]


class ParcoursController(BaseController):

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
        if sort not in {"titre", "version_starter_id", "created_at", "updated_at", "id"}:
            sort = ""
        direction = _query_param(request, "direction", "desc")
        if direction not in ("asc", "desc"):
            direction = "asc"
        limit  = 20
        version_starter_id_raw = _query_param(request, "version_starter_id").strip()
        version_starter_id_f = ""
        if version_starter_id_raw:
            try:
                version_starter_id_f = int(version_starter_id_raw)
            except (TypeError, ValueError):
                version_starter_id_f = ""
        relation_filters = {}
        relation_filters["version_starter_id"] = {"options": [{"id": value, "label": label} for value, label in get_version_starter_choices()]}
        _filters = {}
        if version_starter_id_f != "":
            _filters["version_starter_id"] = version_starter_id_f
        total    = count_parcourss(q or None, filters=_filters or None)
        pagination_state = Pagination(request, total, limit)
        limit = pagination_state.limit
        offset = pagination_state.offset
        empty_context = "search_filters" if q and _filters else ("search" if q else ("filters" if _filters else None))
        parcourss = find_parcourss_paginated(
            q=q or None, sort=sort or None, direction=direction,
            limit=limit, offset=offset, filters=_filters or None,
        )
        pagination = pagination_state.to_dict()
        pagination.update({
            "q": q, "sort": sort, "direction": direction,
            "filters": {"version_starter_id": version_starter_id_f},
        })
        return {
                "parcourss": parcourss,
                "pagination": pagination,
                "empty_context": empty_context,
                "relation_filters": relation_filters,
                "flash": get_flash(get_session_id(request)),
            }

    @staticmethod
    def index(request: Request) -> Response:
        context = ParcoursController._list_context(request)
        template = "parcours/_results.html" if _is_hx_request(request) else "parcours/index.html"
        return BaseController.render(template, context=context, request=request)

    @staticmethod
    def new(request: Request) -> Response:
        form = ParcoursForm(**_parcours_form_options())
        return BaseController.render("parcours/form.html",
            context={
                "form": form,
                "action": "/parcours/create",
                "titre": "Nouveau parcours",
            },
            request=request)

    @staticmethod
    def create(request: Request) -> Response:
        form = ParcoursForm.from_request(request, **_parcours_form_options())
        if not form.is_valid():
            return BaseController.validation_error("parcours/form.html",
                context={
                    "form": form,
                    "action": "/parcours/create",
                    "titre": "Nouveau parcours",
                },
                request=request)
        add_parcours(form.cleaned_data)
        return BaseController.redirect_with_flash(request, "/parcours", "Parcours créé.")

    @staticmethod
    def show(request: Request) -> Response:
        id = ParcoursController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        parcours = get_parcours_by_id(id)
        if parcours is None:
            return BaseController.not_found()
        return BaseController.render("parcours/show.html",
            context={"parcours": parcours, "flash": get_flash(get_session_id(request))},
            request=request)

    @staticmethod
    def edit(request: Request) -> Response:
        id = ParcoursController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        parcours = get_parcours_by_id(id)
        if parcours is None:
            return BaseController.not_found()
        return BaseController.render("parcours/form.html",
            context={
                "form": ParcoursForm(_form_data_from_parcours(parcours), **_parcours_form_options()),
                "action": f"/parcours/update/{id}",
                "titre": "Modifier parcours",
            },
            request=request)

    @staticmethod
    def update(request: Request) -> Response:
        id = ParcoursController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        form = ParcoursForm.from_request(request, **_parcours_form_options())
        if not form.is_valid():
            return BaseController.validation_error("parcours/form.html",
                context={
                    "form": form,
                    "action": f"/parcours/update/{id}",
                    "titre": "Modifier parcours",
                },
                request=request)
        update_parcours(id, form.cleaned_data)
        return BaseController.redirect_with_flash(
            request, f"/parcours/show/{id}", "Parcours mis à jour.")

    @staticmethod
    def destroy(request: Request) -> Response:
        id = ParcoursController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        delete_parcours(id)
        if _is_hx_request(request):
            context = ParcoursController._list_context(request)
            return BaseController.render("parcours/_results.html", context=context, request=request)
        return BaseController.redirect_with_flash(request, "/parcours", "Parcours supprimé.")


    @staticmethod
    def bulk_delete(request: Request) -> Response:
        ids = ParcoursController._parse_bulk_ids(request)
        if not ids:
            return BaseController.redirect_with_flash(request, "/parcours", "Aucun élément sélectionné.")
        return BaseController.render("parcours/bulk_delete_confirm.html",
            context={"ids": ids, "count": len(ids), "flash": get_flash(get_session_id(request))},
            request=request)

    @staticmethod
    def bulk_delete_confirm(request: Request) -> Response:
        ids = ParcoursController._parse_bulk_ids(request)
        if not ids:
            return BaseController.redirect_with_flash(request, "/parcours", "Aucun élément sélectionné.")
        bulk_delete_parcourss(ids)
        count = len(ids)
        return BaseController.redirect_with_flash(
            request, "/parcours",
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
        if sort not in {"titre", "version_starter_id", "created_at", "updated_at", "id"}:
            sort = ""
        direction = _query_param(request, "direction", "desc")
        if direction not in ("asc", "desc"):
            direction = "asc"
        version_starter_id_raw = _query_param(request, "version_starter_id").strip()
        version_starter_id_f = ""
        if version_starter_id_raw:
            try:
                version_starter_id_f = int(version_starter_id_raw)
            except (TypeError, ValueError):
                version_starter_id_f = ""
        _filters = {}
        if version_starter_id_f != "":
            _filters["version_starter_id"] = version_starter_id_f
        rows = find_parcourss_for_export(q=q or None, sort=sort or None, direction=direction, filters=_filters or None)
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_ALL)
        writer.writerow([header for header, _ in _CSV_COLS])
        for row in rows:
            writer.writerow([ParcoursController._csv_escape(str(row.get(key) or "")) for _, key in _CSV_COLS])
        content = output.getvalue().encode("utf-8")
        return Response(
            200,
            content,
            "text/csv; charset=utf-8",
            headers={
                "Content-Disposition": 'attachment; filename="parcourss.csv"',
                "Cache-Control": "no-store",
            },
        )
