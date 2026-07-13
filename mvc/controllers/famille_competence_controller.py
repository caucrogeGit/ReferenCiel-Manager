import csv
import io
from core.http.request import Request
from core.http.response import Response
from core.mvc.controller import BaseController
from core.mvc.view.pagination import Pagination
from mvc.models.famille_competence_model import (
    get_famille_competence_by_id, add_famille_competence, update_famille_competence, delete_famille_competence, bulk_delete_famille_competences,
    count_famille_competences, find_famille_competences_paginated, find_famille_competences_for_export,
    get_referentiel_niveau_classe_choices, get_competence_choices,
    get_famille_competence_competence_ids, add_famille_competence_competence_ids, sync_famille_competence_competence_ids, get_famille_competence_competence_labels_by_famille_competence_id, get_famille_competence_competence_labels,
)
from mvc.forms.famille_competence_form import FamilleCompetenceForm
from core.security.session import get_flash, get_session_id


def _form_data_from_famille_competence(record: dict) -> dict:
    """Convertit les colonnes SQL vers les noms de champs du formulaire."""
    return {
        "code": record.get("Code"),
        "intitule": record.get("Intitule"),
        "referentiel_id": record.get("referentiel_id"),
        "created_at": record.get("CreatedAt"),
        "updated_at": record.get("UpdatedAt"),
    }


def _famille_competence_form_options():
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


class FamilleCompetenceController(BaseController):

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
    def _parse_many_ids(request, field_name):
        raw = request.body.get(field_name, [])
        values = raw if isinstance(raw, list) else ([raw] if raw else [])
        selected = []
        seen = set()
        for value in values:
            try:
                item = int(value)
            except (TypeError, ValueError):
                continue
            if item <= 0 or item in seen:
                continue
            seen.add(item)
            selected.append(item)
        return selected

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
        total    = count_famille_competences(q or None, filters=_filters or None)
        pagination_state = Pagination(request, total, limit)
        limit = pagination_state.limit
        offset = pagination_state.offset
        empty_context = "search_filters" if q and _filters else ("search" if q else ("filters" if _filters else None))
        famille_competences = find_famille_competences_paginated(
            q=q or None, sort=sort or None, direction=direction,
            limit=limit, offset=offset, filters=_filters or None,
        )
        pagination = pagination_state.to_dict()
        pagination.update({
            "q": q, "sort": sort, "direction": direction,
            "filters": {"referentiel_id": referentiel_id_f},
        })
        return {
                "famille_competences": famille_competences,
                "pagination": pagination,
                "empty_context": empty_context,
                "relation_filters": relation_filters,
                "flash": get_flash(get_session_id(request)),
                "competences_by_famille_competence_id": get_famille_competence_competence_labels_by_famille_competence_id([row["Id"] for row in famille_competences]),
            }

    @staticmethod
    def index(request: Request) -> Response:
        context = FamilleCompetenceController._list_context(request)
        template = "app/famille_competence/_results.html" if _is_hx_request(request) else "app/famille_competence/index.html"
        return BaseController.render(template, context=context, request=request)

    @staticmethod
    def new(request: Request) -> Response:
        form = FamilleCompetenceForm(**_famille_competence_form_options())
        return BaseController.render("app/famille_competence/form.html",
            context={
                "form": form,
                "action": "/famille_competence/create",
                "titre": "Nouveau famille_competence",
                "competence_choices": get_competence_choices(),
                "competence_ids_selected": [],
            },
            request=request)

    @staticmethod
    def create(request: Request) -> Response:
        form = FamilleCompetenceForm.from_request(request, **_famille_competence_form_options())
        competence_ids = FamilleCompetenceController._parse_many_ids(request, "competence_ids")
        if not form.is_valid():
            return BaseController.validation_error("app/famille_competence/form.html",
                context={
                    "form": form,
                    "action": "/famille_competence/create",
                    "titre": "Nouveau famille_competence",
                    "competence_choices": get_competence_choices(),
                    "competence_ids_selected": competence_ids,
                },
                request=request)
        created_id = add_famille_competence(form.cleaned_data)
        add_famille_competence_competence_ids(created_id, competence_ids)
        return BaseController.redirect_with_flash(request, "/famille_competence", "FamilleCompetence créé.")

    @staticmethod
    def show(request: Request) -> Response:
        id = FamilleCompetenceController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        famille_competence = get_famille_competence_by_id(id)
        if famille_competence is None:
            return BaseController.not_found()
        competence_labels = get_famille_competence_competence_labels(id)
        return BaseController.render("app/famille_competence/show.html",
            context={"famille_competence": famille_competence, "flash": get_flash(get_session_id(request)), "competence_labels": competence_labels},
            request=request)

    @staticmethod
    def edit(request: Request) -> Response:
        id = FamilleCompetenceController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        famille_competence = get_famille_competence_by_id(id)
        if famille_competence is None:
            return BaseController.not_found()
        return BaseController.render("app/famille_competence/form.html",
            context={
                "form": FamilleCompetenceForm(_form_data_from_famille_competence(famille_competence), **_famille_competence_form_options()),
                "action": f"/famille_competence/update/{id}",
                "titre": "Modifier famille_competence",
                "competence_choices": get_competence_choices(),
                "competence_ids_selected": get_famille_competence_competence_ids(id),
            },
            request=request)

    @staticmethod
    def update(request: Request) -> Response:
        id = FamilleCompetenceController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        form = FamilleCompetenceForm.from_request(request, **_famille_competence_form_options())
        competence_ids = FamilleCompetenceController._parse_many_ids(request, "competence_ids")
        if not form.is_valid():
            return BaseController.validation_error("app/famille_competence/form.html",
                context={
                    "form": form,
                    "action": f"/famille_competence/update/{id}",
                    "titre": "Modifier famille_competence",
                    "competence_choices": get_competence_choices(),
                    "competence_ids_selected": competence_ids,
                },
                request=request)
        update_famille_competence(id, form.cleaned_data)
        sync_famille_competence_competence_ids(id, competence_ids)
        return BaseController.redirect_with_flash(
            request, f"/famille_competence/show/{id}", "FamilleCompetence mis à jour.")

    @staticmethod
    def destroy(request: Request) -> Response:
        id = FamilleCompetenceController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        delete_famille_competence(id)
        if _is_hx_request(request):
            context = FamilleCompetenceController._list_context(request)
            return BaseController.render("app/famille_competence/_results.html", context=context, request=request)
        return BaseController.redirect_with_flash(request, "/famille_competence", "FamilleCompetence supprimé.")


    @staticmethod
    def bulk_delete(request: Request) -> Response:
        ids = FamilleCompetenceController._parse_bulk_ids(request)
        if not ids:
            return BaseController.redirect_with_flash(request, "/famille_competence", "Aucun élément sélectionné.")
        return BaseController.render("app/famille_competence/bulk_delete_confirm.html",
            context={"ids": ids, "count": len(ids), "flash": get_flash(get_session_id(request))},
            request=request)

    @staticmethod
    def bulk_delete_confirm(request: Request) -> Response:
        ids = FamilleCompetenceController._parse_bulk_ids(request)
        if not ids:
            return BaseController.redirect_with_flash(request, "/famille_competence", "Aucun élément sélectionné.")
        bulk_delete_famille_competences(ids)
        count = len(ids)
        return BaseController.redirect_with_flash(
            request, "/famille_competence",
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
        rows = find_famille_competences_for_export(q=q or None, sort=sort or None, direction=direction, filters=_filters or None)
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_ALL)
        writer.writerow([header for header, _ in _CSV_COLS])
        for row in rows:
            writer.writerow([FamilleCompetenceController._csv_escape(str(row.get(key) or "")) for _, key in _CSV_COLS])
        content = output.getvalue().encode("utf-8")
        return Response(
            200,
            content,
            "text/csv; charset=utf-8",
            headers={
                "Content-Disposition": 'attachment; filename="famille_competences.csv"',
                "Cache-Control": "no-store",
            },
        )
