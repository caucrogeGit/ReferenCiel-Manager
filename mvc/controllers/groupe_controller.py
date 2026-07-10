import csv
import io
from core.http.request import Request
from core.http.response import Response
from core.mvc.controller import BaseController
from core.mvc.view.pagination import Pagination
from mvc.models.groupe_model import (
    get_groupe_by_id, add_groupe, update_groupe, delete_groupe, bulk_delete_groupes,
    count_groupes, find_groupes_paginated, find_groupes_for_export,
    get_classe_choices, get_eleve_choices,
    get_groupe_eleve_ids, add_groupe_eleve_ids, sync_groupe_eleve_ids, get_groupe_eleve_labels_by_groupe_id, get_groupe_eleve_labels,
)
from mvc.forms.groupe_form import GroupeForm
from core.security.session import get_flash, get_session_id


def _form_data_from_groupe(record: dict) -> dict:
    """Convertit les colonnes SQL vers les noms de champs du formulaire."""
    return {
        "nom": record.get("Nom"),
        "classe_id": record.get("classe_id"),
        "created_at": record.get("CreatedAt"),
        "updated_at": record.get("UpdatedAt"),
    }


def _groupe_form_options():
    return {
        "classe_id_choices": get_classe_choices(),
    }


def _query_param(request, name, default=""):
    """Retourne le premier paramètre GET, au format parse_qs de Forge."""
    values = request.params.get(name, [default])
    return values[0] if values else default


def _is_hx_request(request):
    """Détecte une requête HTMX locale au CRUD généré."""
    return request.headers.get("HX-Request", "").lower() == "true"


_CSV_COLS = [('Nom', 'Nom'), ('Classe id', 'classe_id_label'), ('Created at', 'CreatedAt'), ('Updated at', 'UpdatedAt')]


class GroupeController(BaseController):

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
        if sort not in {"nom", "classe_id", "created_at", "updated_at", "id"}:
            sort = ""
        direction = _query_param(request, "direction", "desc")
        if direction not in ("asc", "desc"):
            direction = "asc"
        limit  = 20
        classe_id_raw = _query_param(request, "classe_id").strip()
        classe_id_f = ""
        if classe_id_raw:
            try:
                classe_id_f = int(classe_id_raw)
            except (TypeError, ValueError):
                classe_id_f = ""
        relation_filters = {}
        relation_filters["classe_id"] = {"options": [{"id": value, "label": label} for value, label in get_classe_choices()]}
        _filters = {}
        if classe_id_f != "":
            _filters["classe_id"] = classe_id_f
        total    = count_groupes(q or None, filters=_filters or None)
        pagination_state = Pagination(request, total, limit)
        limit = pagination_state.limit
        offset = pagination_state.offset
        empty_context = "search_filters" if q and _filters else ("search" if q else ("filters" if _filters else None))
        groupes = find_groupes_paginated(
            q=q or None, sort=sort or None, direction=direction,
            limit=limit, offset=offset, filters=_filters or None,
        )
        pagination = pagination_state.to_dict()
        pagination.update({
            "q": q, "sort": sort, "direction": direction,
            "filters": {"classe_id": classe_id_f},
        })
        return {
                "groupes": groupes,
                "pagination": pagination,
                "empty_context": empty_context,
                "relation_filters": relation_filters,
                "flash": get_flash(get_session_id(request)),
                "eleves_by_groupe_id": get_groupe_eleve_labels_by_groupe_id([row["Id"] for row in groupes]),
            }

    @staticmethod
    def index(request: Request) -> Response:
        context = GroupeController._list_context(request)
        template = "app/groupe/_results.html" if _is_hx_request(request) else "app/groupe/index.html"
        return BaseController.render(template, context=context, request=request)

    @staticmethod
    def new(request: Request) -> Response:
        form = GroupeForm(**_groupe_form_options())
        return BaseController.render("app/groupe/form.html",
            context={
                "form": form,
                "action": "/groupe/create",
                "titre": "Nouveau groupe",
                "eleve_choices": get_eleve_choices(),
                "eleve_ids_selected": [],
            },
            request=request)

    @staticmethod
    def create(request: Request) -> Response:
        form = GroupeForm.from_request(request, **_groupe_form_options())
        eleve_ids = GroupeController._parse_many_ids(request, "eleve_ids")
        if not form.is_valid():
            return BaseController.validation_error("app/groupe/form.html",
                context={
                    "form": form,
                    "action": "/groupe/create",
                    "titre": "Nouveau groupe",
                    "eleve_choices": get_eleve_choices(),
                    "eleve_ids_selected": eleve_ids,
                },
                request=request)
        created_id = add_groupe(form.cleaned_data)
        add_groupe_eleve_ids(created_id, eleve_ids)
        return BaseController.redirect_with_flash(request, "/groupe", "Groupe créé.")

    @staticmethod
    def show(request: Request) -> Response:
        id = GroupeController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        groupe = get_groupe_by_id(id)
        if groupe is None:
            return BaseController.not_found()
        eleve_labels = get_groupe_eleve_labels(id)
        return BaseController.render("app/groupe/show.html",
            context={"groupe": groupe, "flash": get_flash(get_session_id(request)), "eleve_labels": eleve_labels},
            request=request)

    @staticmethod
    def edit(request: Request) -> Response:
        id = GroupeController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        groupe = get_groupe_by_id(id)
        if groupe is None:
            return BaseController.not_found()
        return BaseController.render("app/groupe/form.html",
            context={
                "form": GroupeForm(_form_data_from_groupe(groupe), **_groupe_form_options()),
                "action": f"/groupe/update/{id}",
                "titre": "Modifier groupe",
                "eleve_choices": get_eleve_choices(),
                "eleve_ids_selected": get_groupe_eleve_ids(id),
            },
            request=request)

    @staticmethod
    def update(request: Request) -> Response:
        id = GroupeController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        form = GroupeForm.from_request(request, **_groupe_form_options())
        eleve_ids = GroupeController._parse_many_ids(request, "eleve_ids")
        if not form.is_valid():
            return BaseController.validation_error("app/groupe/form.html",
                context={
                    "form": form,
                    "action": f"/groupe/update/{id}",
                    "titre": "Modifier groupe",
                    "eleve_choices": get_eleve_choices(),
                    "eleve_ids_selected": eleve_ids,
                },
                request=request)
        update_groupe(id, form.cleaned_data)
        sync_groupe_eleve_ids(id, eleve_ids)
        return BaseController.redirect_with_flash(
            request, f"/groupe/show/{id}", "Groupe mis à jour.")

    @staticmethod
    def destroy(request: Request) -> Response:
        id = GroupeController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        delete_groupe(id)
        if _is_hx_request(request):
            context = GroupeController._list_context(request)
            return BaseController.render("app/groupe/_results.html", context=context, request=request)
        return BaseController.redirect_with_flash(request, "/groupe", "Groupe supprimé.")


    @staticmethod
    def bulk_delete(request: Request) -> Response:
        ids = GroupeController._parse_bulk_ids(request)
        if not ids:
            return BaseController.redirect_with_flash(request, "/groupe", "Aucun élément sélectionné.")
        return BaseController.render("app/groupe/bulk_delete_confirm.html",
            context={"ids": ids, "count": len(ids), "flash": get_flash(get_session_id(request))},
            request=request)

    @staticmethod
    def bulk_delete_confirm(request: Request) -> Response:
        ids = GroupeController._parse_bulk_ids(request)
        if not ids:
            return BaseController.redirect_with_flash(request, "/groupe", "Aucun élément sélectionné.")
        bulk_delete_groupes(ids)
        count = len(ids)
        return BaseController.redirect_with_flash(
            request, "/groupe",
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
        if sort not in {"nom", "classe_id", "created_at", "updated_at", "id"}:
            sort = ""
        direction = _query_param(request, "direction", "desc")
        if direction not in ("asc", "desc"):
            direction = "asc"
        classe_id_raw = _query_param(request, "classe_id").strip()
        classe_id_f = ""
        if classe_id_raw:
            try:
                classe_id_f = int(classe_id_raw)
            except (TypeError, ValueError):
                classe_id_f = ""
        _filters = {}
        if classe_id_f != "":
            _filters["classe_id"] = classe_id_f
        rows = find_groupes_for_export(q=q or None, sort=sort or None, direction=direction, filters=_filters or None)
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_ALL)
        writer.writerow([header for header, _ in _CSV_COLS])
        for row in rows:
            writer.writerow([GroupeController._csv_escape(str(row.get(key) or "")) for _, key in _CSV_COLS])
        content = output.getvalue().encode("utf-8")
        return Response(
            200,
            content,
            "text/csv; charset=utf-8",
            headers={
                "Content-Disposition": 'attachment; filename="groupes.csv"',
                "Cache-Control": "no-store",
            },
        )
