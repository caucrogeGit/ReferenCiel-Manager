import csv
import io
from core.http.request import Request
from core.http.response import Response
from core.mvc.controller import BaseController
from core.mvc.view.pagination import Pagination
from mvc.models.niveau_classe_model import (
    get_niveau_classe_by_id, add_niveau_classe, update_niveau_classe, delete_niveau_classe, bulk_delete_niveau_classes,
    count_niveau_classes, find_niveau_classes_paginated, find_niveau_classes_for_export,
)
from mvc.forms.niveau_classe_form import NiveauClasseForm
from core.security.session import get_flash, get_session_id


def _form_data_from_niveau_classe(record: dict) -> dict:
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


class NiveauClasseController(BaseController):

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
        total    = count_niveau_classes(q or None)
        pagination_state = Pagination(request, total, limit)
        limit = pagination_state.limit
        offset = pagination_state.offset
        empty_context = "search" if q else None
        niveau_classes = find_niveau_classes_paginated(
            q=q or None, sort=sort or None, direction=direction,
            limit=limit, offset=offset,
        )
        pagination = pagination_state.to_dict()
        pagination.update({
            "q": q, "sort": sort, "direction": direction,
            "filters": {},
        })
        return {
                "niveau_classes": niveau_classes,
                "pagination": pagination,
                "empty_context": empty_context,
                "relation_filters": relation_filters,
                "flash": get_flash(get_session_id(request)),
            }

    @staticmethod
    def index(request: Request) -> Response:
        context = NiveauClasseController._list_context(request)
        template = "app/niveau_classe/_results.html" if _is_hx_request(request) else "app/niveau_classe/index.html"
        return BaseController.render(template, context=context, request=request)

    @staticmethod
    def new(request: Request) -> Response:
        form = NiveauClasseForm()
        return BaseController.render("app/niveau_classe/form.html",
            context={
                "form": form,
                "action": "/niveau_classe/create",
                "titre": "Nouveau niveau_classe",
            },
            request=request)

    @staticmethod
    def create(request: Request) -> Response:
        form = NiveauClasseForm.from_request(request)
        if not form.is_valid():
            return BaseController.validation_error("app/niveau_classe/form.html",
                context={
                    "form": form,
                    "action": "/niveau_classe/create",
                    "titre": "Nouveau niveau_classe",
                },
                request=request)
        add_niveau_classe(form.cleaned_data)
        return BaseController.redirect_with_flash(request, "/niveau_classe", "NiveauClasse créé.")

    @staticmethod
    def show(request: Request) -> Response:
        id = NiveauClasseController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        niveau_classe = get_niveau_classe_by_id(id)
        if niveau_classe is None:
            return BaseController.not_found()
        return BaseController.render("app/niveau_classe/show.html",
            context={"niveau_classe": niveau_classe, "flash": get_flash(get_session_id(request))},
            request=request)

    @staticmethod
    def edit(request: Request) -> Response:
        id = NiveauClasseController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        niveau_classe = get_niveau_classe_by_id(id)
        if niveau_classe is None:
            return BaseController.not_found()
        return BaseController.render("app/niveau_classe/form.html",
            context={
                "form": NiveauClasseForm(_form_data_from_niveau_classe(niveau_classe)),
                "action": f"/niveau_classe/update/{id}",
                "titre": "Modifier niveau_classe",
            },
            request=request)

    @staticmethod
    def update(request: Request) -> Response:
        id = NiveauClasseController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        form = NiveauClasseForm.from_request(request)
        if not form.is_valid():
            return BaseController.validation_error("app/niveau_classe/form.html",
                context={
                    "form": form,
                    "action": f"/niveau_classe/update/{id}",
                    "titre": "Modifier niveau_classe",
                },
                request=request)
        update_niveau_classe(id, form.cleaned_data)
        return BaseController.redirect_with_flash(
            request, f"/niveau_classe/show/{id}", "NiveauClasse mis à jour.")

    @staticmethod
    def destroy(request: Request) -> Response:
        id = NiveauClasseController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        delete_niveau_classe(id)
        if _is_hx_request(request):
            context = NiveauClasseController._list_context(request)
            return BaseController.render("app/niveau_classe/_results.html", context=context, request=request)
        return BaseController.redirect_with_flash(request, "/niveau_classe", "NiveauClasse supprimé.")


    @staticmethod
    def bulk_delete(request: Request) -> Response:
        ids = NiveauClasseController._parse_bulk_ids(request)
        if not ids:
            return BaseController.redirect_with_flash(request, "/niveau_classe", "Aucun élément sélectionné.")
        return BaseController.render("app/niveau_classe/bulk_delete_confirm.html",
            context={"ids": ids, "count": len(ids), "flash": get_flash(get_session_id(request))},
            request=request)

    @staticmethod
    def bulk_delete_confirm(request: Request) -> Response:
        ids = NiveauClasseController._parse_bulk_ids(request)
        if not ids:
            return BaseController.redirect_with_flash(request, "/niveau_classe", "Aucun élément sélectionné.")
        bulk_delete_niveau_classes(ids)
        count = len(ids)
        return BaseController.redirect_with_flash(
            request, "/niveau_classe",
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
        rows = find_niveau_classes_for_export(q=q or None, sort=sort or None, direction=direction)
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_ALL)
        writer.writerow([header for header, _ in _CSV_COLS])
        for row in rows:
            writer.writerow([NiveauClasseController._csv_escape(str(row.get(key) or "")) for _, key in _CSV_COLS])
        content = output.getvalue().encode("utf-8")
        return Response(
            200,
            content,
            "text/csv; charset=utf-8",
            headers={
                "Content-Disposition": 'attachment; filename="niveau_classes.csv"',
                "Cache-Control": "no-store",
            },
        )
