import csv
import io
from core.http.request import Request
from core.http.response import Response
from core.mvc.controller import BaseController
from core.mvc.view.pagination import Pagination
from mvc.models.seance_model import (
    get_seance_by_id, add_seance, update_seance, delete_seance, bulk_delete_seances,
    count_seances, find_seances_paginated, find_seances_for_export,
    get_sequence_choices,
)
from mvc.forms.seance_form import SeanceForm
from core.security.session import get_flash, get_session_id


def _form_data_from_seance(record: dict) -> dict:
    """Convertit les colonnes SQL vers les noms de champs du formulaire."""
    return {
        "ordre": record.get("Ordre"),
        "titre": record.get("Titre"),
        "theme": record.get("Theme"),
        "production_attendue": record.get("ProductionAttendue"),
        "sequence_id": record.get("sequence_id"),
    }


def _seance_form_options():
    return {
        "sequence_id_choices": get_sequence_choices(),
    }


def _query_param(request, name, default=""):
    """Retourne le premier paramètre GET, au format parse_qs de Forge."""
    values = request.params.get(name, [default])
    return values[0] if values else default


def _is_hx_request(request):
    """Détecte une requête HTMX locale au CRUD généré."""
    return request.headers.get("HX-Request", "").lower() == "true"


_CSV_COLS = [('Ordre', 'Ordre'), ('Titre', 'Titre'), ('Theme', 'Theme'), ('Production attendue', 'ProductionAttendue'), ('Séquence', 'sequence_id_label')]


class SeanceController(BaseController):

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
        if sort not in {"ordre", "titre", "theme", "production_attendue", "sequence_id", "id"}:
            sort = ""
        direction = _query_param(request, "direction", "desc")
        if direction not in ("asc", "desc"):
            direction = "asc"
        limit  = 20
        sequence_id_raw = _query_param(request, "sequence_id").strip()
        sequence_id_f = ""
        if sequence_id_raw:
            try:
                sequence_id_f = int(sequence_id_raw)
            except (TypeError, ValueError):
                sequence_id_f = ""
        relation_filters = {}
        relation_filters["sequence_id"] = {"options": [{"id": value, "label": label} for value, label in get_sequence_choices()]}
        _filters = {}
        if sequence_id_f != "":
            _filters["sequence_id"] = sequence_id_f
        total    = count_seances(q or None, filters=_filters or None)
        pagination_state = Pagination(request, total, limit)
        limit = pagination_state.limit
        offset = pagination_state.offset
        empty_context = "search_filters" if q and _filters else ("search" if q else ("filters" if _filters else None))
        seances = find_seances_paginated(
            q=q or None, sort=sort or None, direction=direction,
            limit=limit, offset=offset, filters=_filters or None,
        )
        pagination = pagination_state.to_dict()
        pagination.update({
            "q": q, "sort": sort, "direction": direction,
            "filters": {"sequence_id": sequence_id_f},
        })
        return {
                "seances": seances,
                "pagination": pagination,
                "empty_context": empty_context,
                "relation_filters": relation_filters,
                "flash": get_flash(get_session_id(request)),
            }

    @staticmethod
    def index(request: Request) -> Response:
        context = SeanceController._list_context(request)
        template = "app/seance/_results.html" if _is_hx_request(request) else "app/seance/index.html"
        return BaseController.render(template, context=context, request=request)

    @staticmethod
    def new(request: Request) -> Response:
        form = SeanceForm(**_seance_form_options())
        return BaseController.render("app/seance/form.html",
            context={
                "form": form,
                "action": "/seance/create",
                "titre": "Nouvelle séance",
            },
            request=request)

    @staticmethod
    def create(request: Request) -> Response:
        form = SeanceForm.from_request(request, **_seance_form_options())
        if not form.is_valid():
            return BaseController.validation_error("app/seance/form.html",
                context={
                    "form": form,
                    "action": "/seance/create",
                    "titre": "Nouvelle séance",
                },
                request=request)
        add_seance(form.cleaned_data)
        return BaseController.redirect_with_flash(request, "/seance", "Séance créée.")

    @staticmethod
    def show(request: Request) -> Response:
        id = SeanceController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        seance = get_seance_by_id(id)
        if seance is None:
            return BaseController.not_found()
        return BaseController.render("app/seance/show.html",
            context={"seance": seance, "flash": get_flash(get_session_id(request))},
            request=request)

    @staticmethod
    def edit(request: Request) -> Response:
        id = SeanceController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        seance = get_seance_by_id(id)
        if seance is None:
            return BaseController.not_found()
        return BaseController.render("app/seance/form.html",
            context={
                "form": SeanceForm(_form_data_from_seance(seance), **_seance_form_options()),
                "action": f"/seance/update/{id}",
                "titre": "Modifier la séance",
            },
            request=request)

    @staticmethod
    def update(request: Request) -> Response:
        id = SeanceController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        form = SeanceForm.from_request(request, **_seance_form_options())
        if not form.is_valid():
            return BaseController.validation_error("app/seance/form.html",
                context={
                    "form": form,
                    "action": f"/seance/update/{id}",
                    "titre": "Modifier la séance",
                },
                request=request)
        update_seance(id, form.cleaned_data)
        return BaseController.redirect_with_flash(
            request, f"/seance/show/{id}", "Séance mise à jour.")

    @staticmethod
    def destroy(request: Request) -> Response:
        id = SeanceController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        delete_seance(id)
        if _is_hx_request(request):
            context = SeanceController._list_context(request)
            return BaseController.render("app/seance/_results.html", context=context, request=request)
        return BaseController.redirect_with_flash(request, "/seance", "Séance supprimée.")


    @staticmethod
    def bulk_delete(request: Request) -> Response:
        ids = SeanceController._parse_bulk_ids(request)
        if not ids:
            return BaseController.redirect_with_flash(request, "/seance", "Aucun élément sélectionné.")
        return BaseController.render("app/seance/bulk_delete_confirm.html",
            context={"ids": ids, "count": len(ids), "flash": get_flash(get_session_id(request))},
            request=request)

    @staticmethod
    def bulk_delete_confirm(request: Request) -> Response:
        ids = SeanceController._parse_bulk_ids(request)
        if not ids:
            return BaseController.redirect_with_flash(request, "/seance", "Aucun élément sélectionné.")
        bulk_delete_seances(ids)
        count = len(ids)
        return BaseController.redirect_with_flash(
            request, "/seance",
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
        if sort not in {"ordre", "titre", "theme", "production_attendue", "sequence_id", "id"}:
            sort = ""
        direction = _query_param(request, "direction", "desc")
        if direction not in ("asc", "desc"):
            direction = "asc"
        sequence_id_raw = _query_param(request, "sequence_id").strip()
        sequence_id_f = ""
        if sequence_id_raw:
            try:
                sequence_id_f = int(sequence_id_raw)
            except (TypeError, ValueError):
                sequence_id_f = ""
        _filters = {}
        if sequence_id_f != "":
            _filters["sequence_id"] = sequence_id_f
        rows = find_seances_for_export(q=q or None, sort=sort or None, direction=direction, filters=_filters or None)
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_ALL)
        writer.writerow([header for header, _ in _CSV_COLS])
        for row in rows:
            writer.writerow([SeanceController._csv_escape(str(row.get(key) or "")) for _, key in _CSV_COLS])
        content = output.getvalue().encode("utf-8")
        return Response(
            200,
            content,
            "text/csv; charset=utf-8",
            headers={
                "Content-Disposition": 'attachment; filename="seances.csv"',
                "Cache-Control": "no-store",
            },
        )
