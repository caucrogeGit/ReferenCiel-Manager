import csv
import io
from core.http.request import Request
from core.http.response import Response
from core.mvc.controller import BaseController
from core.mvc.view.pagination import Pagination
from mvc.models.starter_welcome_model import (
    get_starter_welcome_by_id, add_starter_welcome, update_starter_welcome, delete_starter_welcome, bulk_delete_starter_welcomes,
    count_starter_welcomes, find_starter_welcomes_paginated, find_starter_welcomes_for_export,
    get_niveau_classe_choices,
)
from mvc.forms.starter_welcome_form import StarterWelcomeForm
from core.security.session import get_flash, get_session_id


def _form_data_from_starter_welcome(record: dict) -> dict:
    """Convertit les colonnes SQL vers les noms de champs du formulaire."""
    return {
        "identifiant": record.get("Identifiant"),
        "titre": record.get("Titre"),
        "presentation": record.get("Presentation"),
        "niveau_classe_id": record.get("niveau_classe_id"),
        "created_at": record.get("CreatedAt"),
        "updated_at": record.get("UpdatedAt"),
    }


def _starter_welcome_form_options():
    return {
        "niveau_classe_id_choices": get_niveau_classe_choices(),
    }


def _query_param(request, name, default=""):
    """Retourne le premier paramètre GET, au format parse_qs de Forge."""
    values = request.params.get(name, [default])
    return values[0] if values else default


def _is_hx_request(request):
    """Détecte une requête HTMX locale au CRUD généré."""
    return request.headers.get("HX-Request", "").lower() == "true"


_CSV_COLS = [('Identifiant', 'Identifiant'), ('Titre', 'Titre'), ('Presentation', 'Presentation'), ('Niveau classe id', 'niveau_classe_id_label'), ('Created at', 'CreatedAt'), ('Updated at', 'UpdatedAt')]


class StarterWelcomeController(BaseController):

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
        if sort not in {"identifiant", "titre", "presentation", "niveau_classe_id", "created_at", "updated_at", "id"}:
            sort = ""
        direction = _query_param(request, "direction", "desc")
        if direction not in ("asc", "desc"):
            direction = "asc"
        limit  = 20
        niveau_classe_id_raw = _query_param(request, "niveau_classe_id").strip()
        niveau_classe_id_f = ""
        if niveau_classe_id_raw:
            try:
                niveau_classe_id_f = int(niveau_classe_id_raw)
            except (TypeError, ValueError):
                niveau_classe_id_f = ""
        relation_filters = {}
        relation_filters["niveau_classe_id"] = {"options": [{"id": value, "label": label} for value, label in get_niveau_classe_choices()]}
        _filters = {}
        if niveau_classe_id_f != "":
            _filters["niveau_classe_id"] = niveau_classe_id_f
        total    = count_starter_welcomes(q or None, filters=_filters or None)
        pagination_state = Pagination(request, total, limit)
        limit = pagination_state.limit
        offset = pagination_state.offset
        empty_context = "search_filters" if q and _filters else ("search" if q else ("filters" if _filters else None))
        starter_welcomes = find_starter_welcomes_paginated(
            q=q or None, sort=sort or None, direction=direction,
            limit=limit, offset=offset, filters=_filters or None,
        )
        pagination = pagination_state.to_dict()
        pagination.update({
            "q": q, "sort": sort, "direction": direction,
            "filters": {"niveau_classe_id": niveau_classe_id_f},
        })
        return {
                "starter_welcomes": starter_welcomes,
                "pagination": pagination,
                "empty_context": empty_context,
                "relation_filters": relation_filters,
                "flash": get_flash(get_session_id(request)),
            }

    @staticmethod
    def index(request: Request) -> Response:
        context = StarterWelcomeController._list_context(request)
        template = "starter_welcome/_results.html" if _is_hx_request(request) else "starter_welcome/index.html"
        return BaseController.render(template, context=context, request=request)

    @staticmethod
    def new(request: Request) -> Response:
        form = StarterWelcomeForm(**_starter_welcome_form_options())
        return BaseController.render("starter_welcome/form.html",
            context={
                "form": form,
                "action": "/starter_welcome/create",
                "titre": "Nouveau starter_welcome",
            },
            request=request)

    @staticmethod
    def create(request: Request) -> Response:
        form = StarterWelcomeForm.from_request(request, **_starter_welcome_form_options())
        if not form.is_valid():
            return BaseController.validation_error("starter_welcome/form.html",
                context={
                    "form": form,
                    "action": "/starter_welcome/create",
                    "titre": "Nouveau starter_welcome",
                },
                request=request)
        add_starter_welcome(form.cleaned_data)
        return BaseController.redirect_with_flash(request, "/starter_welcome", "StarterWelcome créé.")

    @staticmethod
    def show(request: Request) -> Response:
        id = StarterWelcomeController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        starter_welcome = get_starter_welcome_by_id(id)
        if starter_welcome is None:
            return BaseController.not_found()
        return BaseController.render("starter_welcome/show.html",
            context={"starter_welcome": starter_welcome, "flash": get_flash(get_session_id(request))},
            request=request)

    @staticmethod
    def edit(request: Request) -> Response:
        id = StarterWelcomeController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        starter_welcome = get_starter_welcome_by_id(id)
        if starter_welcome is None:
            return BaseController.not_found()
        return BaseController.render("starter_welcome/form.html",
            context={
                "form": StarterWelcomeForm(_form_data_from_starter_welcome(starter_welcome), **_starter_welcome_form_options()),
                "action": f"/starter_welcome/update/{id}",
                "titre": "Modifier starter_welcome",
            },
            request=request)

    @staticmethod
    def update(request: Request) -> Response:
        id = StarterWelcomeController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        form = StarterWelcomeForm.from_request(request, **_starter_welcome_form_options())
        if not form.is_valid():
            return BaseController.validation_error("starter_welcome/form.html",
                context={
                    "form": form,
                    "action": f"/starter_welcome/update/{id}",
                    "titre": "Modifier starter_welcome",
                },
                request=request)
        update_starter_welcome(id, form.cleaned_data)
        return BaseController.redirect_with_flash(
            request, f"/starter_welcome/show/{id}", "StarterWelcome mis à jour.")

    @staticmethod
    def destroy(request: Request) -> Response:
        id = StarterWelcomeController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        delete_starter_welcome(id)
        if _is_hx_request(request):
            context = StarterWelcomeController._list_context(request)
            return BaseController.render("starter_welcome/_results.html", context=context, request=request)
        return BaseController.redirect_with_flash(request, "/starter_welcome", "StarterWelcome supprimé.")


    @staticmethod
    def bulk_delete(request: Request) -> Response:
        ids = StarterWelcomeController._parse_bulk_ids(request)
        if not ids:
            return BaseController.redirect_with_flash(request, "/starter_welcome", "Aucun élément sélectionné.")
        return BaseController.render("starter_welcome/bulk_delete_confirm.html",
            context={"ids": ids, "count": len(ids), "flash": get_flash(get_session_id(request))},
            request=request)

    @staticmethod
    def bulk_delete_confirm(request: Request) -> Response:
        ids = StarterWelcomeController._parse_bulk_ids(request)
        if not ids:
            return BaseController.redirect_with_flash(request, "/starter_welcome", "Aucun élément sélectionné.")
        bulk_delete_starter_welcomes(ids)
        count = len(ids)
        return BaseController.redirect_with_flash(
            request, "/starter_welcome",
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
        if sort not in {"identifiant", "titre", "presentation", "niveau_classe_id", "created_at", "updated_at", "id"}:
            sort = ""
        direction = _query_param(request, "direction", "desc")
        if direction not in ("asc", "desc"):
            direction = "asc"
        niveau_classe_id_raw = _query_param(request, "niveau_classe_id").strip()
        niveau_classe_id_f = ""
        if niveau_classe_id_raw:
            try:
                niveau_classe_id_f = int(niveau_classe_id_raw)
            except (TypeError, ValueError):
                niveau_classe_id_f = ""
        _filters = {}
        if niveau_classe_id_f != "":
            _filters["niveau_classe_id"] = niveau_classe_id_f
        rows = find_starter_welcomes_for_export(q=q or None, sort=sort or None, direction=direction, filters=_filters or None)
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_ALL)
        writer.writerow([header for header, _ in _CSV_COLS])
        for row in rows:
            writer.writerow([StarterWelcomeController._csv_escape(str(row.get(key) or "")) for _, key in _CSV_COLS])
        content = output.getvalue().encode("utf-8")
        return Response(
            200,
            content,
            "text/csv; charset=utf-8",
            headers={
                "Content-Disposition": 'attachment; filename="starter_welcomes.csv"',
                "Cache-Control": "no-store",
            },
        )
