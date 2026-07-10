import csv
import io
from core.http.request import Request
from core.http.response import Response
from core.mvc.controller import BaseController
from core.mvc.view.pagination import Pagination
from mvc.models.version_parcours_model import (
    get_version_parcours_by_id, add_version_parcours, update_version_parcours, delete_version_parcours, bulk_delete_version_parcourss,
    count_version_parcourss, find_version_parcourss_paginated, find_version_parcourss_for_export,
    get_parcours_choices,
)
from mvc.forms.version_parcours_form import VersionParcoursForm
from core.security.session import get_flash, get_session_id


def _form_data_from_version_parcours(record: dict) -> dict:
    """Convertit les colonnes SQL vers les noms de champs du formulaire."""
    return {
        "version": record.get("Version"),
        "statut": record.get("Statut"),
        "parcours_id": record.get("parcours_id"),
        "created_at": record.get("CreatedAt"),
        "updated_at": record.get("UpdatedAt"),
    }


def _version_parcours_form_options():
    return {
        "parcours_id_choices": get_parcours_choices(),
    }


def _query_param(request, name, default=""):
    """Retourne le premier paramètre GET, au format parse_qs de Forge."""
    values = request.params.get(name, [default])
    return values[0] if values else default


def _is_hx_request(request):
    """Détecte une requête HTMX locale au CRUD généré."""
    return request.headers.get("HX-Request", "").lower() == "true"


_CSV_COLS = [('Version', 'Version'), ('Statut', 'Statut'), ('Parcours id', 'parcours_id_label'), ('Created at', 'CreatedAt'), ('Updated at', 'UpdatedAt')]


class VersionParcoursController(BaseController):

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
        if sort not in {"version", "statut", "parcours_id", "created_at", "updated_at", "id"}:
            sort = ""
        direction = _query_param(request, "direction", "desc")
        if direction not in ("asc", "desc"):
            direction = "asc"
        limit  = 20
        parcours_id_raw = _query_param(request, "parcours_id").strip()
        parcours_id_f = ""
        if parcours_id_raw:
            try:
                parcours_id_f = int(parcours_id_raw)
            except (TypeError, ValueError):
                parcours_id_f = ""
        relation_filters = {}
        relation_filters["parcours_id"] = {"options": [{"id": value, "label": label} for value, label in get_parcours_choices()]}
        _filters = {}
        if parcours_id_f != "":
            _filters["parcours_id"] = parcours_id_f
        total    = count_version_parcourss(q or None, filters=_filters or None)
        pagination_state = Pagination(request, total, limit)
        limit = pagination_state.limit
        offset = pagination_state.offset
        empty_context = "search_filters" if q and _filters else ("search" if q else ("filters" if _filters else None))
        version_parcourss = find_version_parcourss_paginated(
            q=q or None, sort=sort or None, direction=direction,
            limit=limit, offset=offset, filters=_filters or None,
        )
        pagination = pagination_state.to_dict()
        pagination.update({
            "q": q, "sort": sort, "direction": direction,
            "filters": {"parcours_id": parcours_id_f},
        })
        return {
                "version_parcourss": version_parcourss,
                "pagination": pagination,
                "empty_context": empty_context,
                "relation_filters": relation_filters,
                "flash": get_flash(get_session_id(request)),
            }

    @staticmethod
    def index(request: Request) -> Response:
        context = VersionParcoursController._list_context(request)
        template = "version_parcours/_results.html" if _is_hx_request(request) else "version_parcours/index.html"
        return BaseController.render(template, context=context, request=request)

    @staticmethod
    def new(request: Request) -> Response:
        form = VersionParcoursForm(**_version_parcours_form_options())
        return BaseController.render("version_parcours/form.html",
            context={
                "form": form,
                "action": "/version_parcours/create",
                "titre": "Nouveau version_parcours",
            },
            request=request)

    @staticmethod
    def create(request: Request) -> Response:
        form = VersionParcoursForm.from_request(request, **_version_parcours_form_options())
        if not form.is_valid():
            return BaseController.validation_error("version_parcours/form.html",
                context={
                    "form": form,
                    "action": "/version_parcours/create",
                    "titre": "Nouveau version_parcours",
                },
                request=request)
        add_version_parcours(form.cleaned_data)
        return BaseController.redirect_with_flash(request, "/version_parcours", "VersionParcours créé.")

    @staticmethod
    def show(request: Request) -> Response:
        id = VersionParcoursController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        version_parcours = get_version_parcours_by_id(id)
        if version_parcours is None:
            return BaseController.not_found()
        return BaseController.render("version_parcours/show.html",
            context={"version_parcours": version_parcours, "flash": get_flash(get_session_id(request))},
            request=request)

    @staticmethod
    def edit(request: Request) -> Response:
        id = VersionParcoursController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        version_parcours = get_version_parcours_by_id(id)
        if version_parcours is None:
            return BaseController.not_found()
        return BaseController.render("version_parcours/form.html",
            context={
                "form": VersionParcoursForm(_form_data_from_version_parcours(version_parcours), **_version_parcours_form_options()),
                "action": f"/version_parcours/update/{id}",
                "titre": "Modifier version_parcours",
            },
            request=request)

    @staticmethod
    def update(request: Request) -> Response:
        id = VersionParcoursController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        form = VersionParcoursForm.from_request(request, **_version_parcours_form_options())
        if not form.is_valid():
            return BaseController.validation_error("version_parcours/form.html",
                context={
                    "form": form,
                    "action": f"/version_parcours/update/{id}",
                    "titre": "Modifier version_parcours",
                },
                request=request)
        update_version_parcours(id, form.cleaned_data)
        return BaseController.redirect_with_flash(
            request, f"/version_parcours/show/{id}", "VersionParcours mis à jour.")

    @staticmethod
    def destroy(request: Request) -> Response:
        id = VersionParcoursController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        delete_version_parcours(id)
        if _is_hx_request(request):
            context = VersionParcoursController._list_context(request)
            return BaseController.render("version_parcours/_results.html", context=context, request=request)
        return BaseController.redirect_with_flash(request, "/version_parcours", "VersionParcours supprimé.")


    @staticmethod
    def bulk_delete(request: Request) -> Response:
        ids = VersionParcoursController._parse_bulk_ids(request)
        if not ids:
            return BaseController.redirect_with_flash(request, "/version_parcours", "Aucun élément sélectionné.")
        return BaseController.render("version_parcours/bulk_delete_confirm.html",
            context={"ids": ids, "count": len(ids), "flash": get_flash(get_session_id(request))},
            request=request)

    @staticmethod
    def bulk_delete_confirm(request: Request) -> Response:
        ids = VersionParcoursController._parse_bulk_ids(request)
        if not ids:
            return BaseController.redirect_with_flash(request, "/version_parcours", "Aucun élément sélectionné.")
        bulk_delete_version_parcourss(ids)
        count = len(ids)
        return BaseController.redirect_with_flash(
            request, "/version_parcours",
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
        if sort not in {"version", "statut", "parcours_id", "created_at", "updated_at", "id"}:
            sort = ""
        direction = _query_param(request, "direction", "desc")
        if direction not in ("asc", "desc"):
            direction = "asc"
        parcours_id_raw = _query_param(request, "parcours_id").strip()
        parcours_id_f = ""
        if parcours_id_raw:
            try:
                parcours_id_f = int(parcours_id_raw)
            except (TypeError, ValueError):
                parcours_id_f = ""
        _filters = {}
        if parcours_id_f != "":
            _filters["parcours_id"] = parcours_id_f
        rows = find_version_parcourss_for_export(q=q or None, sort=sort or None, direction=direction, filters=_filters or None)
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_ALL)
        writer.writerow([header for header, _ in _CSV_COLS])
        for row in rows:
            writer.writerow([VersionParcoursController._csv_escape(str(row.get(key) or "")) for _, key in _CSV_COLS])
        content = output.getvalue().encode("utf-8")
        return Response(
            200,
            content,
            "text/csv; charset=utf-8",
            headers={
                "Content-Disposition": 'attachment; filename="version_parcourss.csv"',
                "Cache-Control": "no-store",
            },
        )
