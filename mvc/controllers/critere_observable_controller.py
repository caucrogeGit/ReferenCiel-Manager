import csv
import io
from core.http.request import Request
from core.http.response import Response
from core.mvc.controller import BaseController
from core.mvc.view.pagination import Pagination
from mvc.models.critere_observable_model import (
    get_critere_observable_by_id, add_critere_observable, update_critere_observable, delete_critere_observable, bulk_delete_critere_observables,
    count_critere_observables, find_critere_observables_paginated, find_critere_observables_for_export,
    get_competence_choices,
)
from mvc.forms.critere_observable_form import CritereObservableForm
from core.security.session import get_flash, get_session_id


def _form_data_from_critere_observable(record: dict) -> dict:
    """Convertit les colonnes SQL vers les noms de champs du formulaire."""
    return {
        "code": record.get("Code"),
        "libelle": record.get("Libelle"),
        "competence_id": record.get("competence_id"),
        "created_at": record.get("CreatedAt"),
        "updated_at": record.get("UpdatedAt"),
    }


def _critere_observable_form_options():
    return {
        "competence_id_choices": get_competence_choices(),
    }


def _query_param(request, name, default=""):
    """Retourne le premier paramètre GET, au format parse_qs de Forge."""
    values = request.params.get(name, [default])
    return values[0] if values else default


def _is_hx_request(request):
    """Détecte une requête HTMX locale au CRUD généré."""
    return request.headers.get("HX-Request", "").lower() == "true"


_CSV_COLS = [('Code', 'Code'), ('Libelle', 'Libelle'), ('Competence id', 'competence_id_label'), ('Created at', 'CreatedAt'), ('Updated at', 'UpdatedAt')]


class CritereObservableController(BaseController):

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
        if sort not in {"code", "libelle", "competence_id", "created_at", "updated_at", "id"}:
            sort = ""
        direction = _query_param(request, "direction", "desc")
        if direction not in ("asc", "desc"):
            direction = "asc"
        limit  = 20
        competence_id_raw = _query_param(request, "competence_id").strip()
        competence_id_f = ""
        if competence_id_raw:
            try:
                competence_id_f = int(competence_id_raw)
            except (TypeError, ValueError):
                competence_id_f = ""
        relation_filters = {}
        relation_filters["competence_id"] = {"options": [{"id": value, "label": label} for value, label in get_competence_choices()]}
        _filters = {}
        if competence_id_f != "":
            _filters["competence_id"] = competence_id_f
        total    = count_critere_observables(q or None, filters=_filters or None)
        pagination_state = Pagination(request, total, limit)
        limit = pagination_state.limit
        offset = pagination_state.offset
        empty_context = "search_filters" if q and _filters else ("search" if q else ("filters" if _filters else None))
        critere_observables = find_critere_observables_paginated(
            q=q or None, sort=sort or None, direction=direction,
            limit=limit, offset=offset, filters=_filters or None,
        )
        pagination = pagination_state.to_dict()
        pagination.update({
            "q": q, "sort": sort, "direction": direction,
            "filters": {"competence_id": competence_id_f},
        })
        return {
                "critere_observables": critere_observables,
                "pagination": pagination,
                "empty_context": empty_context,
                "relation_filters": relation_filters,
                "flash": get_flash(get_session_id(request)),
            }

    @staticmethod
    def index(request: Request) -> Response:
        context = CritereObservableController._list_context(request)
        template = "app/critere_observable/_results.html" if _is_hx_request(request) else "app/critere_observable/index.html"
        return BaseController.render(template, context=context, request=request)

    @staticmethod
    def new(request: Request) -> Response:
        form = CritereObservableForm(**_critere_observable_form_options())
        return BaseController.render("app/critere_observable/form.html",
            context={
                "form": form,
                "action": "/critere_observable/create",
                "titre": "Nouveau critere_observable",
            },
            request=request)

    @staticmethod
    def create(request: Request) -> Response:
        form = CritereObservableForm.from_request(request, **_critere_observable_form_options())
        if not form.is_valid():
            return BaseController.validation_error("app/critere_observable/form.html",
                context={
                    "form": form,
                    "action": "/critere_observable/create",
                    "titre": "Nouveau critere_observable",
                },
                request=request)
        add_critere_observable(form.cleaned_data)
        return BaseController.redirect_with_flash(request, "/critere_observable", "CritereObservable créé.")

    @staticmethod
    def show(request: Request) -> Response:
        id = CritereObservableController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        critere_observable = get_critere_observable_by_id(id)
        if critere_observable is None:
            return BaseController.not_found()
        return BaseController.render("app/critere_observable/show.html",
            context={"critere_observable": critere_observable, "flash": get_flash(get_session_id(request))},
            request=request)

    @staticmethod
    def edit(request: Request) -> Response:
        id = CritereObservableController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        critere_observable = get_critere_observable_by_id(id)
        if critere_observable is None:
            return BaseController.not_found()
        return BaseController.render("app/critere_observable/form.html",
            context={
                "form": CritereObservableForm(_form_data_from_critere_observable(critere_observable), **_critere_observable_form_options()),
                "action": f"/critere_observable/update/{id}",
                "titre": "Modifier critere_observable",
            },
            request=request)

    @staticmethod
    def update(request: Request) -> Response:
        id = CritereObservableController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        form = CritereObservableForm.from_request(request, **_critere_observable_form_options())
        if not form.is_valid():
            return BaseController.validation_error("app/critere_observable/form.html",
                context={
                    "form": form,
                    "action": f"/critere_observable/update/{id}",
                    "titre": "Modifier critere_observable",
                },
                request=request)
        update_critere_observable(id, form.cleaned_data)
        return BaseController.redirect_with_flash(
            request, f"/critere_observable/show/{id}", "CritereObservable mis à jour.")

    @staticmethod
    def destroy(request: Request) -> Response:
        id = CritereObservableController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        delete_critere_observable(id)
        if _is_hx_request(request):
            context = CritereObservableController._list_context(request)
            return BaseController.render("app/critere_observable/_results.html", context=context, request=request)
        return BaseController.redirect_with_flash(request, "/critere_observable", "CritereObservable supprimé.")


    @staticmethod
    def bulk_delete(request: Request) -> Response:
        ids = CritereObservableController._parse_bulk_ids(request)
        if not ids:
            return BaseController.redirect_with_flash(request, "/critere_observable", "Aucun élément sélectionné.")
        return BaseController.render("app/critere_observable/bulk_delete_confirm.html",
            context={"ids": ids, "count": len(ids), "flash": get_flash(get_session_id(request))},
            request=request)

    @staticmethod
    def bulk_delete_confirm(request: Request) -> Response:
        ids = CritereObservableController._parse_bulk_ids(request)
        if not ids:
            return BaseController.redirect_with_flash(request, "/critere_observable", "Aucun élément sélectionné.")
        bulk_delete_critere_observables(ids)
        count = len(ids)
        return BaseController.redirect_with_flash(
            request, "/critere_observable",
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
        if sort not in {"code", "libelle", "competence_id", "created_at", "updated_at", "id"}:
            sort = ""
        direction = _query_param(request, "direction", "desc")
        if direction not in ("asc", "desc"):
            direction = "asc"
        competence_id_raw = _query_param(request, "competence_id").strip()
        competence_id_f = ""
        if competence_id_raw:
            try:
                competence_id_f = int(competence_id_raw)
            except (TypeError, ValueError):
                competence_id_f = ""
        _filters = {}
        if competence_id_f != "":
            _filters["competence_id"] = competence_id_f
        rows = find_critere_observables_for_export(q=q or None, sort=sort or None, direction=direction, filters=_filters or None)
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_ALL)
        writer.writerow([header for header, _ in _CSV_COLS])
        for row in rows:
            writer.writerow([CritereObservableController._csv_escape(str(row.get(key) or "")) for _, key in _CSV_COLS])
        content = output.getvalue().encode("utf-8")
        return Response(
            200,
            content,
            "text/csv; charset=utf-8",
            headers={
                "Content-Disposition": 'attachment; filename="critere_observables.csv"',
                "Cache-Control": "no-store",
            },
        )
