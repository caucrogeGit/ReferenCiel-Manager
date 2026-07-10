import csv
import io
from core.http.request import Request
from core.http.response import Response
from core.mvc.controller import BaseController
from core.mvc.view.pagination import Pagination
from mvc.models.qcm_model import (
    get_qcm_by_id, add_qcm, update_qcm, delete_qcm, bulk_delete_qcms,
    count_qcms, find_qcms_paginated, find_qcms_for_export,
    get_palier_choices,
)
from mvc.forms.qcm_form import QCMForm
from core.security.session import get_flash, get_session_id


def _form_data_from_qcm(record: dict) -> dict:
    """Convertit les colonnes SQL vers les noms de champs du formulaire."""
    return {
        "format_reponse": record.get("FormatReponse"),
        "seuil_validation": record.get("SeuilValidation"),
        "palier_id": record.get("palier_id"),
        "created_at": record.get("CreatedAt"),
        "updated_at": record.get("UpdatedAt"),
    }


def _qcm_form_options():
    return {
        "palier_id_choices": get_palier_choices(),
    }


def _query_param(request, name, default=""):
    """Retourne le premier paramètre GET, au format parse_qs de Forge."""
    values = request.params.get(name, [default])
    return values[0] if values else default


def _is_hx_request(request):
    """Détecte une requête HTMX locale au CRUD généré."""
    return request.headers.get("HX-Request", "").lower() == "true"


_CSV_COLS = [('Format reponse', 'FormatReponse'), ('Seuil validation', 'SeuilValidation'), ('Palier id', 'palier_id_label'), ('Created at', 'CreatedAt'), ('Updated at', 'UpdatedAt')]


class QCMController(BaseController):

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
        if sort not in {"format_reponse", "seuil_validation", "palier_id", "created_at", "updated_at", "id"}:
            sort = ""
        direction = _query_param(request, "direction", "desc")
        if direction not in ("asc", "desc"):
            direction = "asc"
        limit  = 20
        palier_id_raw = _query_param(request, "palier_id").strip()
        palier_id_f = ""
        if palier_id_raw:
            try:
                palier_id_f = int(palier_id_raw)
            except (TypeError, ValueError):
                palier_id_f = ""
        relation_filters = {}
        relation_filters["palier_id"] = {"options": [{"id": value, "label": label} for value, label in get_palier_choices()]}
        _filters = {}
        if palier_id_f != "":
            _filters["palier_id"] = palier_id_f
        total    = count_qcms(q or None, filters=_filters or None)
        pagination_state = Pagination(request, total, limit)
        limit = pagination_state.limit
        offset = pagination_state.offset
        empty_context = "search_filters" if q and _filters else ("search" if q else ("filters" if _filters else None))
        qcms = find_qcms_paginated(
            q=q or None, sort=sort or None, direction=direction,
            limit=limit, offset=offset, filters=_filters or None,
        )
        pagination = pagination_state.to_dict()
        pagination.update({
            "q": q, "sort": sort, "direction": direction,
            "filters": {"palier_id": palier_id_f},
        })
        return {
                "qcms": qcms,
                "pagination": pagination,
                "empty_context": empty_context,
                "relation_filters": relation_filters,
                "flash": get_flash(get_session_id(request)),
            }

    @staticmethod
    def index(request: Request) -> Response:
        context = QCMController._list_context(request)
        template = "app/qcm/_results.html" if _is_hx_request(request) else "app/qcm/index.html"
        return BaseController.render(template, context=context, request=request)

    @staticmethod
    def new(request: Request) -> Response:
        form = QCMForm(**_qcm_form_options())
        return BaseController.render("app/qcm/form.html",
            context={
                "form": form,
                "action": "/qcm/create",
                "titre": "Nouveau qcm",
            },
            request=request)

    @staticmethod
    def create(request: Request) -> Response:
        form = QCMForm.from_request(request, **_qcm_form_options())
        if not form.is_valid():
            return BaseController.validation_error("app/qcm/form.html",
                context={
                    "form": form,
                    "action": "/qcm/create",
                    "titre": "Nouveau qcm",
                },
                request=request)
        add_qcm(form.cleaned_data)
        return BaseController.redirect_with_flash(request, "/qcm", "QCM créé.")

    @staticmethod
    def show(request: Request) -> Response:
        id = QCMController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        qcm = get_qcm_by_id(id)
        if qcm is None:
            return BaseController.not_found()
        return BaseController.render("app/qcm/show.html",
            context={"qcm": qcm, "flash": get_flash(get_session_id(request))},
            request=request)

    @staticmethod
    def edit(request: Request) -> Response:
        id = QCMController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        qcm = get_qcm_by_id(id)
        if qcm is None:
            return BaseController.not_found()
        return BaseController.render("app/qcm/form.html",
            context={
                "form": QCMForm(_form_data_from_qcm(qcm), **_qcm_form_options()),
                "action": f"/qcm/update/{id}",
                "titre": "Modifier qcm",
            },
            request=request)

    @staticmethod
    def update(request: Request) -> Response:
        id = QCMController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        form = QCMForm.from_request(request, **_qcm_form_options())
        if not form.is_valid():
            return BaseController.validation_error("app/qcm/form.html",
                context={
                    "form": form,
                    "action": f"/qcm/update/{id}",
                    "titre": "Modifier qcm",
                },
                request=request)
        update_qcm(id, form.cleaned_data)
        return BaseController.redirect_with_flash(
            request, f"/qcm/show/{id}", "QCM mis à jour.")

    @staticmethod
    def destroy(request: Request) -> Response:
        id = QCMController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        delete_qcm(id)
        if _is_hx_request(request):
            context = QCMController._list_context(request)
            return BaseController.render("app/qcm/_results.html", context=context, request=request)
        return BaseController.redirect_with_flash(request, "/qcm", "QCM supprimé.")


    @staticmethod
    def bulk_delete(request: Request) -> Response:
        ids = QCMController._parse_bulk_ids(request)
        if not ids:
            return BaseController.redirect_with_flash(request, "/qcm", "Aucun élément sélectionné.")
        return BaseController.render("app/qcm/bulk_delete_confirm.html",
            context={"ids": ids, "count": len(ids), "flash": get_flash(get_session_id(request))},
            request=request)

    @staticmethod
    def bulk_delete_confirm(request: Request) -> Response:
        ids = QCMController._parse_bulk_ids(request)
        if not ids:
            return BaseController.redirect_with_flash(request, "/qcm", "Aucun élément sélectionné.")
        bulk_delete_qcms(ids)
        count = len(ids)
        return BaseController.redirect_with_flash(
            request, "/qcm",
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
        if sort not in {"format_reponse", "seuil_validation", "palier_id", "created_at", "updated_at", "id"}:
            sort = ""
        direction = _query_param(request, "direction", "desc")
        if direction not in ("asc", "desc"):
            direction = "asc"
        palier_id_raw = _query_param(request, "palier_id").strip()
        palier_id_f = ""
        if palier_id_raw:
            try:
                palier_id_f = int(palier_id_raw)
            except (TypeError, ValueError):
                palier_id_f = ""
        _filters = {}
        if palier_id_f != "":
            _filters["palier_id"] = palier_id_f
        rows = find_qcms_for_export(q=q or None, sort=sort or None, direction=direction, filters=_filters or None)
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_ALL)
        writer.writerow([header for header, _ in _CSV_COLS])
        for row in rows:
            writer.writerow([QCMController._csv_escape(str(row.get(key) or "")) for _, key in _CSV_COLS])
        content = output.getvalue().encode("utf-8")
        return Response(
            200,
            content,
            "text/csv; charset=utf-8",
            headers={
                "Content-Disposition": 'attachment; filename="qcms.csv"',
                "Cache-Control": "no-store",
            },
        )
