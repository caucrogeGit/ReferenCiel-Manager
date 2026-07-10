import csv
import io
from core.http.request import Request
from core.http.response import Response
from core.mvc.controller import BaseController
from core.mvc.view.pagination import Pagination
from mvc.models.version_starter_model import (
    get_version_starter_by_id, add_version_starter, update_version_starter, delete_version_starter, bulk_delete_version_starters,
    count_version_starters, find_version_starters_paginated, find_version_starters_for_export,
    get_starter_welcome_choices,
)
from mvc.forms.version_starter_form import VersionStarterForm
from core.security.session import get_flash, get_session_id


def _form_data_from_version_starter(record: dict) -> dict:
    """Convertit les colonnes SQL vers les noms de champs du formulaire."""
    return {
        "version": record.get("Version"),
        "statut": record.get("Statut"),
        "activite_glissante": record.get("ActiviteGlissante"),
        "ordre_impose": record.get("OrdreImpose"),
        "starter_id": record.get("starter_id"),
        "created_at": record.get("CreatedAt"),
        "updated_at": record.get("UpdatedAt"),
    }


def _version_starter_form_options():
    return {
        "starter_id_choices": get_starter_welcome_choices(),
    }


def _query_param(request, name, default=""):
    """Retourne le premier paramètre GET, au format parse_qs de Forge."""
    values = request.params.get(name, [default])
    return values[0] if values else default


def _is_hx_request(request):
    """Détecte une requête HTMX locale au CRUD généré."""
    return request.headers.get("HX-Request", "").lower() == "true"


_CSV_COLS = [('Version', 'Version'), ('Statut', 'Statut'), ('Activite glissante', 'ActiviteGlissante'), ('Ordre impose', 'OrdreImpose'), ('Starter id', 'starter_id_label'), ('Created at', 'CreatedAt'), ('Updated at', 'UpdatedAt')]


class VersionStarterController(BaseController):

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
        if sort not in {"version", "statut", "activite_glissante", "ordre_impose", "starter_id", "created_at", "updated_at", "id"}:
            sort = ""
        direction = _query_param(request, "direction", "desc")
        if direction not in ("asc", "desc"):
            direction = "asc"
        limit  = 20
        starter_id_raw = _query_param(request, "starter_id").strip()
        starter_id_f = ""
        if starter_id_raw:
            try:
                starter_id_f = int(starter_id_raw)
            except (TypeError, ValueError):
                starter_id_f = ""
        relation_filters = {}
        relation_filters["starter_id"] = {"options": [{"id": value, "label": label} for value, label in get_starter_welcome_choices()]}
        _filters = {}
        if starter_id_f != "":
            _filters["starter_id"] = starter_id_f
        total    = count_version_starters(q or None, filters=_filters or None)
        pagination_state = Pagination(request, total, limit)
        limit = pagination_state.limit
        offset = pagination_state.offset
        empty_context = "search_filters" if q and _filters else ("search" if q else ("filters" if _filters else None))
        version_starters = find_version_starters_paginated(
            q=q or None, sort=sort or None, direction=direction,
            limit=limit, offset=offset, filters=_filters or None,
        )
        pagination = pagination_state.to_dict()
        pagination.update({
            "q": q, "sort": sort, "direction": direction,
            "filters": {"starter_id": starter_id_f},
        })
        return {
                "version_starters": version_starters,
                "pagination": pagination,
                "empty_context": empty_context,
                "relation_filters": relation_filters,
                "flash": get_flash(get_session_id(request)),
            }

    @staticmethod
    def index(request: Request) -> Response:
        context = VersionStarterController._list_context(request)
        template = "version_starter/_results.html" if _is_hx_request(request) else "version_starter/index.html"
        return BaseController.render(template, context=context, request=request)

    @staticmethod
    def new(request: Request) -> Response:
        form = VersionStarterForm(**_version_starter_form_options())
        return BaseController.render("version_starter/form.html",
            context={
                "form": form,
                "action": "/version_starter/create",
                "titre": "Nouveau version_starter",
            },
            request=request)

    @staticmethod
    def create(request: Request) -> Response:
        form = VersionStarterForm.from_request(request, **_version_starter_form_options())
        if not form.is_valid():
            return BaseController.validation_error("version_starter/form.html",
                context={
                    "form": form,
                    "action": "/version_starter/create",
                    "titre": "Nouveau version_starter",
                },
                request=request)
        add_version_starter(form.cleaned_data)
        return BaseController.redirect_with_flash(request, "/version_starter", "VersionStarter créé.")

    @staticmethod
    def show(request: Request) -> Response:
        id = VersionStarterController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        version_starter = get_version_starter_by_id(id)
        if version_starter is None:
            return BaseController.not_found()
        return BaseController.render("version_starter/show.html",
            context={"version_starter": version_starter, "flash": get_flash(get_session_id(request))},
            request=request)

    @staticmethod
    def edit(request: Request) -> Response:
        id = VersionStarterController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        version_starter = get_version_starter_by_id(id)
        if version_starter is None:
            return BaseController.not_found()
        return BaseController.render("version_starter/form.html",
            context={
                "form": VersionStarterForm(_form_data_from_version_starter(version_starter), **_version_starter_form_options()),
                "action": f"/version_starter/update/{id}",
                "titre": "Modifier version_starter",
            },
            request=request)

    @staticmethod
    def update(request: Request) -> Response:
        id = VersionStarterController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        form = VersionStarterForm.from_request(request, **_version_starter_form_options())
        if not form.is_valid():
            return BaseController.validation_error("version_starter/form.html",
                context={
                    "form": form,
                    "action": f"/version_starter/update/{id}",
                    "titre": "Modifier version_starter",
                },
                request=request)
        update_version_starter(id, form.cleaned_data)
        return BaseController.redirect_with_flash(
            request, f"/version_starter/show/{id}", "VersionStarter mis à jour.")

    @staticmethod
    def destroy(request: Request) -> Response:
        id = VersionStarterController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        delete_version_starter(id)
        if _is_hx_request(request):
            context = VersionStarterController._list_context(request)
            return BaseController.render("version_starter/_results.html", context=context, request=request)
        return BaseController.redirect_with_flash(request, "/version_starter", "VersionStarter supprimé.")


    @staticmethod
    def bulk_delete(request: Request) -> Response:
        ids = VersionStarterController._parse_bulk_ids(request)
        if not ids:
            return BaseController.redirect_with_flash(request, "/version_starter", "Aucun élément sélectionné.")
        return BaseController.render("version_starter/bulk_delete_confirm.html",
            context={"ids": ids, "count": len(ids), "flash": get_flash(get_session_id(request))},
            request=request)

    @staticmethod
    def bulk_delete_confirm(request: Request) -> Response:
        ids = VersionStarterController._parse_bulk_ids(request)
        if not ids:
            return BaseController.redirect_with_flash(request, "/version_starter", "Aucun élément sélectionné.")
        bulk_delete_version_starters(ids)
        count = len(ids)
        return BaseController.redirect_with_flash(
            request, "/version_starter",
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
        if sort not in {"version", "statut", "activite_glissante", "ordre_impose", "starter_id", "created_at", "updated_at", "id"}:
            sort = ""
        direction = _query_param(request, "direction", "desc")
        if direction not in ("asc", "desc"):
            direction = "asc"
        starter_id_raw = _query_param(request, "starter_id").strip()
        starter_id_f = ""
        if starter_id_raw:
            try:
                starter_id_f = int(starter_id_raw)
            except (TypeError, ValueError):
                starter_id_f = ""
        _filters = {}
        if starter_id_f != "":
            _filters["starter_id"] = starter_id_f
        rows = find_version_starters_for_export(q=q or None, sort=sort or None, direction=direction, filters=_filters or None)
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_ALL)
        writer.writerow([header for header, _ in _CSV_COLS])
        for row in rows:
            writer.writerow([VersionStarterController._csv_escape(str(row.get(key) or "")) for _, key in _CSV_COLS])
        content = output.getvalue().encode("utf-8")
        return Response(
            200,
            content,
            "text/csv; charset=utf-8",
            headers={
                "Content-Disposition": 'attachment; filename="version_starters.csv"',
                "Cache-Control": "no-store",
            },
        )
