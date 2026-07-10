import csv
import io
from core.http.request import Request
from core.http.response import Response
from core.mvc.controller import BaseController
from core.mvc.view.pagination import Pagination
from mvc.models.reponse_qcm_model import (
    get_reponse_qcm_by_id, add_reponse_qcm, update_reponse_qcm, delete_reponse_qcm, bulk_delete_reponse_qcms,
    count_reponse_qcms, find_reponse_qcms_paginated, find_reponse_qcms_for_export,
    get_tentative_qcm_choices, get_question_qcm_choices, get_choix_qcm_choices,
)
from mvc.forms.reponse_qcm_form import ReponseQCMForm
from core.security.session import get_flash, get_session_id


def _form_data_from_reponse_qcm(record: dict) -> dict:
    """Convertit les colonnes SQL vers les noms de champs du formulaire."""
    return {
        "est_correcte": record.get("EstCorrecte"),
        "tentative_id": record.get("tentative_id"),
        "question_id": record.get("question_id"),
        "choix_id": record.get("choix_id"),
        "created_at": record.get("CreatedAt"),
        "updated_at": record.get("UpdatedAt"),
    }


def _reponse_qcm_form_options():
    return {
        "tentative_id_choices": get_tentative_qcm_choices(),
        "question_id_choices": get_question_qcm_choices(),
        "choix_id_choices": get_choix_qcm_choices(),
    }


def _query_param(request, name, default=""):
    """Retourne le premier paramètre GET, au format parse_qs de Forge."""
    values = request.params.get(name, [default])
    return values[0] if values else default


def _is_hx_request(request):
    """Détecte une requête HTMX locale au CRUD généré."""
    return request.headers.get("HX-Request", "").lower() == "true"


_CSV_COLS = [('Est correcte', 'EstCorrecte'), ('Tentative id', 'tentative_id_label'), ('Question id', 'question_id_label'), ('Choix id', 'choix_id_label'), ('Created at', 'CreatedAt'), ('Updated at', 'UpdatedAt')]


class ReponseQCMController(BaseController):

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
        if sort not in {"est_correcte", "tentative_id", "question_id", "choix_id", "created_at", "updated_at", "id"}:
            sort = ""
        direction = _query_param(request, "direction", "desc")
        if direction not in ("asc", "desc"):
            direction = "asc"
        limit  = 20
        tentative_id_raw = _query_param(request, "tentative_id").strip()
        tentative_id_f = ""
        if tentative_id_raw:
            try:
                tentative_id_f = int(tentative_id_raw)
            except (TypeError, ValueError):
                tentative_id_f = ""
        question_id_raw = _query_param(request, "question_id").strip()
        question_id_f = ""
        if question_id_raw:
            try:
                question_id_f = int(question_id_raw)
            except (TypeError, ValueError):
                question_id_f = ""
        choix_id_raw = _query_param(request, "choix_id").strip()
        choix_id_f = ""
        if choix_id_raw:
            try:
                choix_id_f = int(choix_id_raw)
            except (TypeError, ValueError):
                choix_id_f = ""
        relation_filters = {}
        relation_filters["tentative_id"] = {"options": [{"id": value, "label": label} for value, label in get_tentative_qcm_choices()]}
        relation_filters["question_id"] = {"options": [{"id": value, "label": label} for value, label in get_question_qcm_choices()]}
        relation_filters["choix_id"] = {"options": [{"id": value, "label": label} for value, label in get_choix_qcm_choices()]}
        _filters = {}
        if tentative_id_f != "":
            _filters["tentative_id"] = tentative_id_f
        if question_id_f != "":
            _filters["question_id"] = question_id_f
        if choix_id_f != "":
            _filters["choix_id"] = choix_id_f
        total    = count_reponse_qcms(q or None, filters=_filters or None)
        pagination_state = Pagination(request, total, limit)
        limit = pagination_state.limit
        offset = pagination_state.offset
        empty_context = "search_filters" if q and _filters else ("search" if q else ("filters" if _filters else None))
        reponse_qcms = find_reponse_qcms_paginated(
            q=q or None, sort=sort or None, direction=direction,
            limit=limit, offset=offset, filters=_filters or None,
        )
        pagination = pagination_state.to_dict()
        pagination.update({
            "q": q, "sort": sort, "direction": direction,
            "filters": {"tentative_id": tentative_id_f, "question_id": question_id_f, "choix_id": choix_id_f},
        })
        return {
                "reponse_qcms": reponse_qcms,
                "pagination": pagination,
                "empty_context": empty_context,
                "relation_filters": relation_filters,
                "flash": get_flash(get_session_id(request)),
            }

    @staticmethod
    def index(request: Request) -> Response:
        context = ReponseQCMController._list_context(request)
        template = "reponse_qcm/_results.html" if _is_hx_request(request) else "reponse_qcm/index.html"
        return BaseController.render(template, context=context, request=request)

    @staticmethod
    def new(request: Request) -> Response:
        form = ReponseQCMForm(**_reponse_qcm_form_options())
        return BaseController.render("reponse_qcm/form.html",
            context={
                "form": form,
                "action": "/reponse_qcm/create",
                "titre": "Nouveau reponse_qcm",
            },
            request=request)

    @staticmethod
    def create(request: Request) -> Response:
        form = ReponseQCMForm.from_request(request, **_reponse_qcm_form_options())
        if not form.is_valid():
            return BaseController.validation_error("reponse_qcm/form.html",
                context={
                    "form": form,
                    "action": "/reponse_qcm/create",
                    "titre": "Nouveau reponse_qcm",
                },
                request=request)
        add_reponse_qcm(form.cleaned_data)
        return BaseController.redirect_with_flash(request, "/reponse_qcm", "ReponseQCM créé.")

    @staticmethod
    def show(request: Request) -> Response:
        id = ReponseQCMController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        reponse_qcm = get_reponse_qcm_by_id(id)
        if reponse_qcm is None:
            return BaseController.not_found()
        return BaseController.render("reponse_qcm/show.html",
            context={"reponse_qcm": reponse_qcm, "flash": get_flash(get_session_id(request))},
            request=request)

    @staticmethod
    def edit(request: Request) -> Response:
        id = ReponseQCMController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        reponse_qcm = get_reponse_qcm_by_id(id)
        if reponse_qcm is None:
            return BaseController.not_found()
        return BaseController.render("reponse_qcm/form.html",
            context={
                "form": ReponseQCMForm(_form_data_from_reponse_qcm(reponse_qcm), **_reponse_qcm_form_options()),
                "action": f"/reponse_qcm/update/{id}",
                "titre": "Modifier reponse_qcm",
            },
            request=request)

    @staticmethod
    def update(request: Request) -> Response:
        id = ReponseQCMController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        form = ReponseQCMForm.from_request(request, **_reponse_qcm_form_options())
        if not form.is_valid():
            return BaseController.validation_error("reponse_qcm/form.html",
                context={
                    "form": form,
                    "action": f"/reponse_qcm/update/{id}",
                    "titre": "Modifier reponse_qcm",
                },
                request=request)
        update_reponse_qcm(id, form.cleaned_data)
        return BaseController.redirect_with_flash(
            request, f"/reponse_qcm/show/{id}", "ReponseQCM mis à jour.")

    @staticmethod
    def destroy(request: Request) -> Response:
        id = ReponseQCMController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        delete_reponse_qcm(id)
        if _is_hx_request(request):
            context = ReponseQCMController._list_context(request)
            return BaseController.render("reponse_qcm/_results.html", context=context, request=request)
        return BaseController.redirect_with_flash(request, "/reponse_qcm", "ReponseQCM supprimé.")


    @staticmethod
    def bulk_delete(request: Request) -> Response:
        ids = ReponseQCMController._parse_bulk_ids(request)
        if not ids:
            return BaseController.redirect_with_flash(request, "/reponse_qcm", "Aucun élément sélectionné.")
        return BaseController.render("reponse_qcm/bulk_delete_confirm.html",
            context={"ids": ids, "count": len(ids), "flash": get_flash(get_session_id(request))},
            request=request)

    @staticmethod
    def bulk_delete_confirm(request: Request) -> Response:
        ids = ReponseQCMController._parse_bulk_ids(request)
        if not ids:
            return BaseController.redirect_with_flash(request, "/reponse_qcm", "Aucun élément sélectionné.")
        bulk_delete_reponse_qcms(ids)
        count = len(ids)
        return BaseController.redirect_with_flash(
            request, "/reponse_qcm",
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
        if sort not in {"est_correcte", "tentative_id", "question_id", "choix_id", "created_at", "updated_at", "id"}:
            sort = ""
        direction = _query_param(request, "direction", "desc")
        if direction not in ("asc", "desc"):
            direction = "asc"
        tentative_id_raw = _query_param(request, "tentative_id").strip()
        tentative_id_f = ""
        if tentative_id_raw:
            try:
                tentative_id_f = int(tentative_id_raw)
            except (TypeError, ValueError):
                tentative_id_f = ""
        question_id_raw = _query_param(request, "question_id").strip()
        question_id_f = ""
        if question_id_raw:
            try:
                question_id_f = int(question_id_raw)
            except (TypeError, ValueError):
                question_id_f = ""
        choix_id_raw = _query_param(request, "choix_id").strip()
        choix_id_f = ""
        if choix_id_raw:
            try:
                choix_id_f = int(choix_id_raw)
            except (TypeError, ValueError):
                choix_id_f = ""
        _filters = {}
        if tentative_id_f != "":
            _filters["tentative_id"] = tentative_id_f
        if question_id_f != "":
            _filters["question_id"] = question_id_f
        if choix_id_f != "":
            _filters["choix_id"] = choix_id_f
        rows = find_reponse_qcms_for_export(q=q or None, sort=sort or None, direction=direction, filters=_filters or None)
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_ALL)
        writer.writerow([header for header, _ in _CSV_COLS])
        for row in rows:
            writer.writerow([ReponseQCMController._csv_escape(str(row.get(key) or "")) for _, key in _CSV_COLS])
        content = output.getvalue().encode("utf-8")
        return Response(
            200,
            content,
            "text/csv; charset=utf-8",
            headers={
                "Content-Disposition": 'attachment; filename="reponse_qcms.csv"',
                "Cache-Control": "no-store",
            },
        )
