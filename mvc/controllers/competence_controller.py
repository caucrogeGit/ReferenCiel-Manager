import csv
import io
from core.http.request import Request
from core.http.response import Response
from core.mvc.controller import BaseController
from core.mvc.view.pagination import Pagination
from mvc.models.competence_model import (
    get_competence_by_id, add_competence, update_competence, delete_competence, bulk_delete_competences,
    count_competences, find_competences_paginated, find_competences_for_export,
    get_referentiel_niveau_classe_choices,
)
from mvc.forms.competence_form import CompetenceForm
from core.security.session import get_flash, get_session_id


def _form_data_from_competence(record: dict) -> dict:
    """Convertit les colonnes SQL vers les noms de champs du formulaire."""
    return {
        "code": record.get("Code"),
        "intitule": record.get("Intitule"),
        "referentiel_id": record.get("referentiel_id"),
        "created_at": record.get("CreatedAt"),
        "updated_at": record.get("UpdatedAt"),
    }


def _competence_form_options():
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


_CSV_COLS = [('Code', 'Code'), ('Intitule', 'Intitule'), ('Referentiel id', 'referentiel_id_label'), ('Created at', 'CreatedAt'), ('Updated at', 'UpdatedAt')]


class CompetenceController(BaseController):

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
        if sort not in {"code", "intitule", "referentiel_id", "created_at", "updated_at", "id"}:
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
        total    = count_competences(q or None, filters=_filters or None)
        pagination_state = Pagination(request, total, limit)
        limit = pagination_state.limit
        offset = pagination_state.offset
        empty_context = "search_filters" if q and _filters else ("search" if q else ("filters" if _filters else None))
        competences = find_competences_paginated(
            q=q or None, sort=sort or None, direction=direction,
            limit=limit, offset=offset, filters=_filters or None,
        )
        pagination = pagination_state.to_dict()
        pagination.update({
            "q": q, "sort": sort, "direction": direction,
            "filters": {"referentiel_id": referentiel_id_f},
        })
        return {
                "competences": competences,
                "pagination": pagination,
                "empty_context": empty_context,
                "relation_filters": relation_filters,
                "flash": get_flash(get_session_id(request)),
            }

    @staticmethod
    def index(request: Request) -> Response:
        context = CompetenceController._list_context(request)
        template = "app/competence/_results.html" if _is_hx_request(request) else "app/competence/index.html"
        return BaseController.render(template, context=context, request=request)

    @staticmethod
    def new(request: Request) -> Response:
        form = CompetenceForm(**_competence_form_options())
        return BaseController.render("app/competence/form.html",
            context={
                "form": form,
                "action": "/competence/create",
                "titre": "Nouveau competence",
            },
            request=request)

    @staticmethod
    def create(request: Request) -> Response:
        form = CompetenceForm.from_request(request, **_competence_form_options())
        if not form.is_valid():
            return BaseController.validation_error("app/competence/form.html",
                context={
                    "form": form,
                    "action": "/competence/create",
                    "titre": "Nouveau competence",
                },
                request=request)
        add_competence(form.cleaned_data)
        return BaseController.redirect_with_flash(request, "/competence", "Competence créé.")

    @staticmethod
    def show(request: Request) -> Response:
        id = CompetenceController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        competence = get_competence_by_id(id)
        if competence is None:
            return BaseController.not_found()
        return BaseController.render("app/competence/show.html",
            context={"competence": competence, "flash": get_flash(get_session_id(request))},
            request=request)

    @staticmethod
    def edit(request: Request) -> Response:
        id = CompetenceController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        competence = get_competence_by_id(id)
        if competence is None:
            return BaseController.not_found()
        return BaseController.render("app/competence/form.html",
            context={
                "form": CompetenceForm(_form_data_from_competence(competence), **_competence_form_options()),
                "action": f"/competence/update/{id}",
                "titre": "Modifier competence",
            },
            request=request)

    @staticmethod
    def update(request: Request) -> Response:
        id = CompetenceController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        form = CompetenceForm.from_request(request, **_competence_form_options())
        if not form.is_valid():
            return BaseController.validation_error("app/competence/form.html",
                context={
                    "form": form,
                    "action": f"/competence/update/{id}",
                    "titre": "Modifier competence",
                },
                request=request)
        update_competence(id, form.cleaned_data)
        return BaseController.redirect_with_flash(
            request, f"/competence/show/{id}", "Competence mis à jour.")

    @staticmethod
    def destroy(request: Request) -> Response:
        id = CompetenceController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        delete_competence(id)
        if _is_hx_request(request):
            context = CompetenceController._list_context(request)
            return BaseController.render("app/competence/_results.html", context=context, request=request)
        return BaseController.redirect_with_flash(request, "/competence", "Competence supprimé.")


    @staticmethod
    def bulk_delete(request: Request) -> Response:
        ids = CompetenceController._parse_bulk_ids(request)
        if not ids:
            return BaseController.redirect_with_flash(request, "/competence", "Aucun élément sélectionné.")
        return BaseController.render("app/competence/bulk_delete_confirm.html",
            context={"ids": ids, "count": len(ids), "flash": get_flash(get_session_id(request))},
            request=request)

    @staticmethod
    def bulk_delete_confirm(request: Request) -> Response:
        ids = CompetenceController._parse_bulk_ids(request)
        if not ids:
            return BaseController.redirect_with_flash(request, "/competence", "Aucun élément sélectionné.")
        bulk_delete_competences(ids)
        count = len(ids)
        return BaseController.redirect_with_flash(
            request, "/competence",
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
        if sort not in {"code", "intitule", "referentiel_id", "created_at", "updated_at", "id"}:
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
        rows = find_competences_for_export(q=q or None, sort=sort or None, direction=direction, filters=_filters or None)
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_ALL)
        writer.writerow([header for header, _ in _CSV_COLS])
        for row in rows:
            writer.writerow([CompetenceController._csv_escape(str(row.get(key) or "")) for _, key in _CSV_COLS])
        content = output.getvalue().encode("utf-8")
        return Response(
            200,
            content,
            "text/csv; charset=utf-8",
            headers={
                "Content-Disposition": 'attachment; filename="competences.csv"',
                "Cache-Control": "no-store",
            },
        )
