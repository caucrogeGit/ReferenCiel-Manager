import csv
import io
from core.http.request import Request
from core.http.response import Response
from core.mvc.controller import BaseController
from core.mvc.view.pagination import Pagination
from mvc.models.pole_activite_model import (
    get_pole_activite_by_id, add_pole_activite, update_pole_activite, delete_pole_activite, bulk_delete_pole_activites,
    count_pole_activites, find_pole_activites_paginated, find_pole_activites_for_export,
    get_referentiel_niveau_classe_choices,
)
from mvc.forms.pole_activite_form import PoleActiviteForm
from core.security.session import get_flash, get_session_id


def _form_data_from_pole_activite(record: dict) -> dict:
    """Convertit les colonnes SQL vers les noms de champs du formulaire."""
    return {
        "intitule": record.get("Intitule"),
        "referentiel_id": record.get("referentiel_id"),
        "created_at": record.get("CreatedAt"),
        "updated_at": record.get("UpdatedAt"),
    }


def _pole_activite_form_options():
    return {
        "referentiel_id_choices": get_referentiel_niveau_classe_choices(),
    }


def _query_param(request, name, default=""):
    """Retourne le premier paramètre GET, au format parse_qs de Forge."""
    values = request.params.get(name, [default])
    return values[0] if values else default


def _is_hx_request(request):
    """Détecte une requête HTMX locale au CRUD généré."""
    return request.headers.get("HX-Request", "").lower() == "true"


_CSV_COLS = [('Intitule', 'Intitule'), ('Referentiel id', 'referentiel_id_label'), ('Created at', 'CreatedAt'), ('Updated at', 'UpdatedAt')]


class PoleActiviteController(BaseController):

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
        if sort not in {"intitule", "referentiel_id", "created_at", "updated_at", "id"}:
            sort = ""
        direction = _query_param(request, "direction", "desc")
        if direction not in ("asc", "desc"):
            direction = "asc"
        limit  = 20
        referentiel_id_raw = _query_param(request, "referentiel_id").strip()
        referentiel_id_f = ""
        if referentiel_id_raw:
            try:
                referentiel_id_f = int(referentiel_id_raw)
            except (TypeError, ValueError):
                referentiel_id_f = ""
        relation_filters = {}
        relation_filters["referentiel_id"] = {"options": [{"id": value, "label": label} for value, label in get_referentiel_niveau_classe_choices()]}
        _filters = {}
        if referentiel_id_f != "":
            _filters["referentiel_id"] = referentiel_id_f
        total    = count_pole_activites(q or None, filters=_filters or None)
        pagination_state = Pagination(request, total, limit)
        limit = pagination_state.limit
        offset = pagination_state.offset
        empty_context = "search_filters" if q and _filters else ("search" if q else ("filters" if _filters else None))
        pole_activites = find_pole_activites_paginated(
            q=q or None, sort=sort or None, direction=direction,
            limit=limit, offset=offset, filters=_filters or None,
        )
        pagination = pagination_state.to_dict()
        pagination.update({
            "q": q, "sort": sort, "direction": direction,
            "filters": {"referentiel_id": referentiel_id_f},
        })
        return {
                "pole_activites": pole_activites,
                "pagination": pagination,
                "empty_context": empty_context,
                "relation_filters": relation_filters,
                "flash": get_flash(get_session_id(request)),
            }

    @staticmethod
    def index(request: Request) -> Response:
        context = PoleActiviteController._list_context(request)
        template = "app/pole_activite/_results.html" if _is_hx_request(request) else "app/pole_activite/index.html"
        return BaseController.render(template, context=context, request=request)

    @staticmethod
    def new(request: Request) -> Response:
        form = PoleActiviteForm(**_pole_activite_form_options())
        return BaseController.render("app/pole_activite/form.html",
            context={
                "form": form,
                "action": "/pole_activite/create",
                "titre": "Nouveau pole_activite",
            },
            request=request)

    @staticmethod
    def create(request: Request) -> Response:
        form = PoleActiviteForm.from_request(request, **_pole_activite_form_options())
        if not form.is_valid():
            return BaseController.validation_error("app/pole_activite/form.html",
                context={
                    "form": form,
                    "action": "/pole_activite/create",
                    "titre": "Nouveau pole_activite",
                },
                request=request)
        add_pole_activite(form.cleaned_data)
        return BaseController.redirect_with_flash(request, "/pole_activite", "PoleActivite créé.")

    @staticmethod
    def show(request: Request) -> Response:
        id = PoleActiviteController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        pole_activite = get_pole_activite_by_id(id)
        if pole_activite is None:
            return BaseController.not_found()
        return BaseController.render("app/pole_activite/show.html",
            context={"pole_activite": pole_activite, "flash": get_flash(get_session_id(request))},
            request=request)

    @staticmethod
    def edit(request: Request) -> Response:
        id = PoleActiviteController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        pole_activite = get_pole_activite_by_id(id)
        if pole_activite is None:
            return BaseController.not_found()
        return BaseController.render("app/pole_activite/form.html",
            context={
                "form": PoleActiviteForm(_form_data_from_pole_activite(pole_activite), **_pole_activite_form_options()),
                "action": f"/pole_activite/update/{id}",
                "titre": "Modifier pole_activite",
            },
            request=request)

    @staticmethod
    def update(request: Request) -> Response:
        id = PoleActiviteController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        form = PoleActiviteForm.from_request(request, **_pole_activite_form_options())
        if not form.is_valid():
            return BaseController.validation_error("app/pole_activite/form.html",
                context={
                    "form": form,
                    "action": f"/pole_activite/update/{id}",
                    "titre": "Modifier pole_activite",
                },
                request=request)
        update_pole_activite(id, form.cleaned_data)
        return BaseController.redirect_with_flash(
            request, f"/pole_activite/show/{id}", "PoleActivite mis à jour.")

    @staticmethod
    def destroy(request: Request) -> Response:
        id = PoleActiviteController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        delete_pole_activite(id)
        if _is_hx_request(request):
            context = PoleActiviteController._list_context(request)
            return BaseController.render("app/pole_activite/_results.html", context=context, request=request)
        return BaseController.redirect_with_flash(request, "/pole_activite", "PoleActivite supprimé.")


    @staticmethod
    def bulk_delete(request: Request) -> Response:
        ids = PoleActiviteController._parse_bulk_ids(request)
        if not ids:
            return BaseController.redirect_with_flash(request, "/pole_activite", "Aucun élément sélectionné.")
        return BaseController.render("app/pole_activite/bulk_delete_confirm.html",
            context={"ids": ids, "count": len(ids), "flash": get_flash(get_session_id(request))},
            request=request)

    @staticmethod
    def bulk_delete_confirm(request: Request) -> Response:
        ids = PoleActiviteController._parse_bulk_ids(request)
        if not ids:
            return BaseController.redirect_with_flash(request, "/pole_activite", "Aucun élément sélectionné.")
        bulk_delete_pole_activites(ids)
        count = len(ids)
        return BaseController.redirect_with_flash(
            request, "/pole_activite",
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
        if sort not in {"intitule", "referentiel_id", "created_at", "updated_at", "id"}:
            sort = ""
        direction = _query_param(request, "direction", "desc")
        if direction not in ("asc", "desc"):
            direction = "asc"
        referentiel_id_raw = _query_param(request, "referentiel_id").strip()
        referentiel_id_f = ""
        if referentiel_id_raw:
            try:
                referentiel_id_f = int(referentiel_id_raw)
            except (TypeError, ValueError):
                referentiel_id_f = ""
        _filters = {}
        if referentiel_id_f != "":
            _filters["referentiel_id"] = referentiel_id_f
        rows = find_pole_activites_for_export(q=q or None, sort=sort or None, direction=direction, filters=_filters or None)
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_ALL)
        writer.writerow([header for header, _ in _CSV_COLS])
        for row in rows:
            writer.writerow([PoleActiviteController._csv_escape(str(row.get(key) or "")) for _, key in _CSV_COLS])
        content = output.getvalue().encode("utf-8")
        return Response(
            200,
            content,
            "text/csv; charset=utf-8",
            headers={
                "Content-Disposition": 'attachment; filename="pole_activites.csv"',
                "Cache-Control": "no-store",
            },
        )
