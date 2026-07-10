import csv
import io
from core.http.request import Request
from core.http.response import Response
from core.mvc.controller import BaseController
from core.mvc.view.pagination import Pagination
from mvc.models.choix_qcm_model import (
    get_choix_qcm_by_id, add_choix_qcm, update_choix_qcm, delete_choix_qcm, bulk_delete_choix_qcms,
    count_choix_qcms, find_choix_qcms_paginated, find_choix_qcms_for_export,
    get_question_qcm_choices,
)
from mvc.forms.choix_qcm_form import ChoixQCMForm
from core.security.session import get_flash, get_session_id


def _form_data_from_choix_qcm(record: dict) -> dict:
    """Convertit les colonnes SQL vers les noms de champs du formulaire."""
    return {
        "lettre": record.get("Lettre"),
        "texte": record.get("Texte"),
        "question_id": record.get("question_id"),
        "created_at": record.get("CreatedAt"),
        "updated_at": record.get("UpdatedAt"),
    }


def _choix_qcm_form_options():
    return {
        "question_id_choices": get_question_qcm_choices(),
    }


def _query_param(request, name, default=""):
    """Retourne le premier paramètre GET, au format parse_qs de Forge."""
    values = request.params.get(name, [default])
    return values[0] if values else default


def _is_hx_request(request):
    """Détecte une requête HTMX locale au CRUD généré."""
    return request.headers.get("HX-Request", "").lower() == "true"


_CSV_COLS = [('Lettre', 'Lettre'), ('Texte', 'Texte'), ('Question id', 'question_id_label'), ('Created at', 'CreatedAt'), ('Updated at', 'UpdatedAt')]


class ChoixQCMController(BaseController):

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
        if sort not in {"lettre", "texte", "question_id", "created_at", "updated_at", "id"}:
            sort = ""
        direction = _query_param(request, "direction", "desc")
        if direction not in ("asc", "desc"):
            direction = "asc"
        limit  = 20
        question_id_raw = _query_param(request, "question_id").strip()
        question_id_f = ""
        if question_id_raw:
            try:
                question_id_f = int(question_id_raw)
            except (TypeError, ValueError):
                question_id_f = ""
        relation_filters = {}
        relation_filters["question_id"] = {"options": [{"id": value, "label": label} for value, label in get_question_qcm_choices()]}
        _filters = {}
        if question_id_f != "":
            _filters["question_id"] = question_id_f
        total    = count_choix_qcms(q or None, filters=_filters or None)
        pagination_state = Pagination(request, total, limit)
        limit = pagination_state.limit
        offset = pagination_state.offset
        empty_context = "search_filters" if q and _filters else ("search" if q else ("filters" if _filters else None))
        choix_qcms = find_choix_qcms_paginated(
            q=q or None, sort=sort or None, direction=direction,
            limit=limit, offset=offset, filters=_filters or None,
        )
        pagination = pagination_state.to_dict()
        pagination.update({
            "q": q, "sort": sort, "direction": direction,
            "filters": {"question_id": question_id_f},
        })
        return {
                "choix_qcms": choix_qcms,
                "pagination": pagination,
                "empty_context": empty_context,
                "relation_filters": relation_filters,
                "flash": get_flash(get_session_id(request)),
            }

    @staticmethod
    def index(request: Request) -> Response:
        context = ChoixQCMController._list_context(request)
        template = "app/choix_qcm/_results.html" if _is_hx_request(request) else "app/choix_qcm/index.html"
        return BaseController.render(template, context=context, request=request)

    @staticmethod
    def new(request: Request) -> Response:
        form = ChoixQCMForm(**_choix_qcm_form_options())
        return BaseController.render("app/choix_qcm/form.html",
            context={
                "form": form,
                "action": "/choix_qcm/create",
                "titre": "Nouveau choix_qcm",
            },
            request=request)

    @staticmethod
    def create(request: Request) -> Response:
        form = ChoixQCMForm.from_request(request, **_choix_qcm_form_options())
        if not form.is_valid():
            return BaseController.validation_error("app/choix_qcm/form.html",
                context={
                    "form": form,
                    "action": "/choix_qcm/create",
                    "titre": "Nouveau choix_qcm",
                },
                request=request)
        add_choix_qcm(form.cleaned_data)
        return BaseController.redirect_with_flash(request, "/choix_qcm", "ChoixQCM créé.")

    @staticmethod
    def show(request: Request) -> Response:
        id = ChoixQCMController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        choix_qcm = get_choix_qcm_by_id(id)
        if choix_qcm is None:
            return BaseController.not_found()
        return BaseController.render("app/choix_qcm/show.html",
            context={"choix_qcm": choix_qcm, "flash": get_flash(get_session_id(request))},
            request=request)

    @staticmethod
    def edit(request: Request) -> Response:
        id = ChoixQCMController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        choix_qcm = get_choix_qcm_by_id(id)
        if choix_qcm is None:
            return BaseController.not_found()
        return BaseController.render("app/choix_qcm/form.html",
            context={
                "form": ChoixQCMForm(_form_data_from_choix_qcm(choix_qcm), **_choix_qcm_form_options()),
                "action": f"/choix_qcm/update/{id}",
                "titre": "Modifier choix_qcm",
            },
            request=request)

    @staticmethod
    def update(request: Request) -> Response:
        id = ChoixQCMController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        form = ChoixQCMForm.from_request(request, **_choix_qcm_form_options())
        if not form.is_valid():
            return BaseController.validation_error("app/choix_qcm/form.html",
                context={
                    "form": form,
                    "action": f"/choix_qcm/update/{id}",
                    "titre": "Modifier choix_qcm",
                },
                request=request)
        update_choix_qcm(id, form.cleaned_data)
        return BaseController.redirect_with_flash(
            request, f"/choix_qcm/show/{id}", "ChoixQCM mis à jour.")

    @staticmethod
    def destroy(request: Request) -> Response:
        id = ChoixQCMController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        delete_choix_qcm(id)
        if _is_hx_request(request):
            context = ChoixQCMController._list_context(request)
            return BaseController.render("app/choix_qcm/_results.html", context=context, request=request)
        return BaseController.redirect_with_flash(request, "/choix_qcm", "ChoixQCM supprimé.")


    @staticmethod
    def bulk_delete(request: Request) -> Response:
        ids = ChoixQCMController._parse_bulk_ids(request)
        if not ids:
            return BaseController.redirect_with_flash(request, "/choix_qcm", "Aucun élément sélectionné.")
        return BaseController.render("app/choix_qcm/bulk_delete_confirm.html",
            context={"ids": ids, "count": len(ids), "flash": get_flash(get_session_id(request))},
            request=request)

    @staticmethod
    def bulk_delete_confirm(request: Request) -> Response:
        ids = ChoixQCMController._parse_bulk_ids(request)
        if not ids:
            return BaseController.redirect_with_flash(request, "/choix_qcm", "Aucun élément sélectionné.")
        bulk_delete_choix_qcms(ids)
        count = len(ids)
        return BaseController.redirect_with_flash(
            request, "/choix_qcm",
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
        if sort not in {"lettre", "texte", "question_id", "created_at", "updated_at", "id"}:
            sort = ""
        direction = _query_param(request, "direction", "desc")
        if direction not in ("asc", "desc"):
            direction = "asc"
        question_id_raw = _query_param(request, "question_id").strip()
        question_id_f = ""
        if question_id_raw:
            try:
                question_id_f = int(question_id_raw)
            except (TypeError, ValueError):
                question_id_f = ""
        _filters = {}
        if question_id_f != "":
            _filters["question_id"] = question_id_f
        rows = find_choix_qcms_for_export(q=q or None, sort=sort or None, direction=direction, filters=_filters or None)
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_ALL)
        writer.writerow([header for header, _ in _CSV_COLS])
        for row in rows:
            writer.writerow([ChoixQCMController._csv_escape(str(row.get(key) or "")) for _, key in _CSV_COLS])
        content = output.getvalue().encode("utf-8")
        return Response(
            200,
            content,
            "text/csv; charset=utf-8",
            headers={
                "Content-Disposition": 'attachment; filename="choix_qcms.csv"',
                "Cache-Control": "no-store",
            },
        )
