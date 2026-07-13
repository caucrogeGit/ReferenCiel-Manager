import csv
import io
from core.http.request import Request
from core.http.response import Response
from core.mvc.controller import BaseController
from core.mvc.view.pagination import Pagination
from mvc.models.formation_model import (
    get_formation_by_id, add_formation, update_formation, delete_formation, bulk_delete_formations,
    count_formations, find_formations_paginated, find_formations_for_export,
)
from mvc.forms.formation_form import FormationForm
from core.security.session import get_flash, get_session_id


def _form_data_from_formation(record: dict) -> dict:
    """Convertit les colonnes SQL vers les noms de champs du formulaire."""
    return {
        "code": record.get("Code"),
        "intitule": record.get("Intitule"),
        "created_at": record.get("CreatedAt"),
        "updated_at": record.get("UpdatedAt"),
    }


def _query_param(request, name, default=""):
    """Retourne le premier paramètre GET, au format parse_qs de Forge."""
    values = request.params.get(name, [default])
    return values[0] if values else default


def _is_hx_request(request):
    """Détecte une requête HTMX locale au CRUD généré."""
    return request.headers.get("HX-Request", "").lower() == "true"


_CSV_COLS = [('Code', 'Code'), ('Intitule', 'Intitule'), ('Created at', 'CreatedAt'), ('Updated at', 'UpdatedAt')]


class FormationController(BaseController):

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
        if sort not in {"code", "intitule", "created_at", "updated_at", "id"}:
            sort = ""
        direction = _query_param(request, "direction", "desc")
        if direction not in ("asc", "desc"):
            direction = "asc"
        limit  = 20
        relation_filters = {}
        total    = count_formations(q or None)
        pagination_state = Pagination(request, total, limit)
        limit = pagination_state.limit
        offset = pagination_state.offset
        empty_context = "search" if q else None
        formations = find_formations_paginated(
            q=q or None, sort=sort or None, direction=direction,
            limit=limit, offset=offset,
        )
        pagination = pagination_state.to_dict()
        pagination.update({
            "q": q, "sort": sort, "direction": direction,
            "filters": {},
        })
        return {
                "formations": formations,
                "pagination": pagination,
                "empty_context": empty_context,
                "relation_filters": relation_filters,
                "flash": get_flash(get_session_id(request)),
            }

    @staticmethod
    def index(request: Request) -> Response:
        context = FormationController._list_context(request)
        template = "app/formation/_results.html" if _is_hx_request(request) else "app/formation/index.html"
        return BaseController.render(template, context=context, request=request)

    @staticmethod
    def new(request: Request) -> Response:
        form = FormationForm()
        return BaseController.render("app/formation/form.html",
            context={
                "form": form,
                "action": "/formation/create",
                "titre": "Nouveau formation",
            },
            request=request)

    @staticmethod
    def create(request: Request) -> Response:
        form = FormationForm.from_request(request)
        if not form.is_valid():
            return BaseController.validation_error("app/formation/form.html",
                context={
                    "form": form,
                    "action": "/formation/create",
                    "titre": "Nouveau formation",
                },
                request=request)
        add_formation(form.cleaned_data)
        return BaseController.redirect_with_flash(request, "/formation", "Formation créé.")

    @staticmethod
    def show(request: Request) -> Response:
        id = FormationController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        formation = get_formation_by_id(id)
        if formation is None:
            return BaseController.not_found()
        return BaseController.render("app/formation/show.html",
            context={"formation": formation, "flash": get_flash(get_session_id(request))},
            request=request)

    @staticmethod
    def edit(request: Request) -> Response:
        id = FormationController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        formation = get_formation_by_id(id)
        if formation is None:
            return BaseController.not_found()
        return BaseController.render("app/formation/form.html",
            context={
                "form": FormationForm(_form_data_from_formation(formation)),
                "action": f"/formation/update/{id}",
                "titre": "Modifier formation",
            },
            request=request)

    @staticmethod
    def update(request: Request) -> Response:
        id = FormationController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        form = FormationForm.from_request(request)
        if not form.is_valid():
            return BaseController.validation_error("app/formation/form.html",
                context={
                    "form": form,
                    "action": f"/formation/update/{id}",
                    "titre": "Modifier formation",
                },
                request=request)
        update_formation(id, form.cleaned_data)
        return BaseController.redirect_with_flash(
            request, f"/formation/show/{id}", "Formation mis à jour.")

    @staticmethod
    def destroy(request: Request) -> Response:
        id = FormationController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        delete_formation(id)
        if _is_hx_request(request):
            context = FormationController._list_context(request)
            return BaseController.render("app/formation/_results.html", context=context, request=request)
        return BaseController.redirect_with_flash(request, "/formation", "Formation supprimé.")


    @staticmethod
    def bulk_delete(request: Request) -> Response:
        ids = FormationController._parse_bulk_ids(request)
        if not ids:
            return BaseController.redirect_with_flash(request, "/formation", "Aucun élément sélectionné.")
        return BaseController.render("app/formation/bulk_delete_confirm.html",
            context={"ids": ids, "count": len(ids), "flash": get_flash(get_session_id(request))},
            request=request)

    @staticmethod
    def bulk_delete_confirm(request: Request) -> Response:
        ids = FormationController._parse_bulk_ids(request)
        if not ids:
            return BaseController.redirect_with_flash(request, "/formation", "Aucun élément sélectionné.")
        bulk_delete_formations(ids)
        count = len(ids)
        return BaseController.redirect_with_flash(
            request, "/formation",
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
        if sort not in {"code", "intitule", "created_at", "updated_at", "id"}:
            sort = ""
        direction = _query_param(request, "direction", "desc")
        if direction not in ("asc", "desc"):
            direction = "asc"
        rows = find_formations_for_export(q=q or None, sort=sort or None, direction=direction)
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_ALL)
        writer.writerow([header for header, _ in _CSV_COLS])
        for row in rows:
            writer.writerow([FormationController._csv_escape(str(row.get(key) or "")) for _, key in _CSV_COLS])
        content = output.getvalue().encode("utf-8")
        return Response(
            200,
            content,
            "text/csv; charset=utf-8",
            headers={
                "Content-Disposition": 'attachment; filename="formations.csv"',
                "Cache-Control": "no-store",
            },
        )
