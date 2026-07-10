import csv
import io
from core.http.request import Request
from core.http.response import Response
from core.mvc.controller import BaseController
from core.mvc.view.pagination import Pagination
from mvc.models.depot_eleve_model import (
    get_depot_eleve_by_id, add_depot_eleve, update_depot_eleve, delete_depot_eleve, bulk_delete_depot_eleves,
    count_depot_eleves, find_depot_eleves_paginated, find_depot_eleves_for_export,
    get_progression_palier_choices, get_activite_choices,
)
from mvc.forms.depot_eleve_form import DepotEleveForm
from core.security.session import get_flash, get_session_id


def _form_data_from_depot_eleve(record: dict) -> dict:
    """Convertit les colonnes SQL vers les noms de champs du formulaire."""
    return {
        "fichier": record.get("Fichier"),
        "commentaire": record.get("Commentaire"),
        "date_depot": record.get("DateDepot"),
        "progression_palier_id": record.get("progression_palier_id"),
        "activite_id": record.get("activite_id"),
        "created_at": record.get("CreatedAt"),
        "updated_at": record.get("UpdatedAt"),
    }


def _depot_eleve_form_options():
    return {
        "progression_palier_id_choices": get_progression_palier_choices(),
        "activite_id_choices": get_activite_choices(),
    }


def _query_param(request, name, default=""):
    """Retourne le premier paramètre GET, au format parse_qs de Forge."""
    values = request.params.get(name, [default])
    return values[0] if values else default


def _is_hx_request(request):
    """Détecte une requête HTMX locale au CRUD généré."""
    return request.headers.get("HX-Request", "").lower() == "true"


_CSV_COLS = [('Fichier', 'Fichier'), ('Commentaire', 'Commentaire'), ('Date depot', 'DateDepot'), ('Progression palier id', 'progression_palier_id_label'), ('Activite id', 'activite_id_label'), ('Created at', 'CreatedAt'), ('Updated at', 'UpdatedAt')]


class DepotEleveController(BaseController):

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
        if sort not in {"fichier", "commentaire", "date_depot", "progression_palier_id", "activite_id", "created_at", "updated_at", "id"}:
            sort = ""
        direction = _query_param(request, "direction", "desc")
        if direction not in ("asc", "desc"):
            direction = "asc"
        limit  = 20
        progression_palier_id_raw = _query_param(request, "progression_palier_id").strip()
        progression_palier_id_f = ""
        if progression_palier_id_raw:
            try:
                progression_palier_id_f = int(progression_palier_id_raw)
            except (TypeError, ValueError):
                progression_palier_id_f = ""
        activite_id_raw = _query_param(request, "activite_id").strip()
        activite_id_f = ""
        if activite_id_raw:
            try:
                activite_id_f = int(activite_id_raw)
            except (TypeError, ValueError):
                activite_id_f = ""
        relation_filters = {}
        relation_filters["progression_palier_id"] = {"options": [{"id": value, "label": label} for value, label in get_progression_palier_choices()]}
        relation_filters["activite_id"] = {"options": [{"id": value, "label": label} for value, label in get_activite_choices()]}
        _filters = {}
        if progression_palier_id_f != "":
            _filters["progression_palier_id"] = progression_palier_id_f
        if activite_id_f != "":
            _filters["activite_id"] = activite_id_f
        total    = count_depot_eleves(q or None, filters=_filters or None)
        pagination_state = Pagination(request, total, limit)
        limit = pagination_state.limit
        offset = pagination_state.offset
        empty_context = "search_filters" if q and _filters else ("search" if q else ("filters" if _filters else None))
        depot_eleves = find_depot_eleves_paginated(
            q=q or None, sort=sort or None, direction=direction,
            limit=limit, offset=offset, filters=_filters or None,
        )
        pagination = pagination_state.to_dict()
        pagination.update({
            "q": q, "sort": sort, "direction": direction,
            "filters": {"progression_palier_id": progression_palier_id_f, "activite_id": activite_id_f},
        })
        return {
                "depot_eleves": depot_eleves,
                "pagination": pagination,
                "empty_context": empty_context,
                "relation_filters": relation_filters,
                "flash": get_flash(get_session_id(request)),
            }

    @staticmethod
    def index(request: Request) -> Response:
        context = DepotEleveController._list_context(request)
        template = "depot_eleve/_results.html" if _is_hx_request(request) else "depot_eleve/index.html"
        return BaseController.render(template, context=context, request=request)

    @staticmethod
    def new(request: Request) -> Response:
        form = DepotEleveForm(**_depot_eleve_form_options())
        return BaseController.render("depot_eleve/form.html",
            context={
                "form": form,
                "action": "/depot_eleve/create",
                "titre": "Nouveau depot_eleve",
            },
            request=request)

    @staticmethod
    def create(request: Request) -> Response:
        form = DepotEleveForm.from_request(request, **_depot_eleve_form_options())
        if not form.is_valid():
            return BaseController.validation_error("depot_eleve/form.html",
                context={
                    "form": form,
                    "action": "/depot_eleve/create",
                    "titre": "Nouveau depot_eleve",
                },
                request=request)
        add_depot_eleve(form.cleaned_data)
        return BaseController.redirect_with_flash(request, "/depot_eleve", "DepotEleve créé.")

    @staticmethod
    def show(request: Request) -> Response:
        id = DepotEleveController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        depot_eleve = get_depot_eleve_by_id(id)
        if depot_eleve is None:
            return BaseController.not_found()
        return BaseController.render("depot_eleve/show.html",
            context={"depot_eleve": depot_eleve, "flash": get_flash(get_session_id(request))},
            request=request)

    @staticmethod
    def edit(request: Request) -> Response:
        id = DepotEleveController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        depot_eleve = get_depot_eleve_by_id(id)
        if depot_eleve is None:
            return BaseController.not_found()
        return BaseController.render("depot_eleve/form.html",
            context={
                "form": DepotEleveForm(_form_data_from_depot_eleve(depot_eleve), **_depot_eleve_form_options()),
                "action": f"/depot_eleve/update/{id}",
                "titre": "Modifier depot_eleve",
            },
            request=request)

    @staticmethod
    def update(request: Request) -> Response:
        id = DepotEleveController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        form = DepotEleveForm.from_request(request, **_depot_eleve_form_options())
        if not form.is_valid():
            return BaseController.validation_error("depot_eleve/form.html",
                context={
                    "form": form,
                    "action": f"/depot_eleve/update/{id}",
                    "titre": "Modifier depot_eleve",
                },
                request=request)
        update_depot_eleve(id, form.cleaned_data)
        return BaseController.redirect_with_flash(
            request, f"/depot_eleve/show/{id}", "DepotEleve mis à jour.")

    @staticmethod
    def destroy(request: Request) -> Response:
        id = DepotEleveController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        delete_depot_eleve(id)
        if _is_hx_request(request):
            context = DepotEleveController._list_context(request)
            return BaseController.render("depot_eleve/_results.html", context=context, request=request)
        return BaseController.redirect_with_flash(request, "/depot_eleve", "DepotEleve supprimé.")


    @staticmethod
    def bulk_delete(request: Request) -> Response:
        ids = DepotEleveController._parse_bulk_ids(request)
        if not ids:
            return BaseController.redirect_with_flash(request, "/depot_eleve", "Aucun élément sélectionné.")
        return BaseController.render("depot_eleve/bulk_delete_confirm.html",
            context={"ids": ids, "count": len(ids), "flash": get_flash(get_session_id(request))},
            request=request)

    @staticmethod
    def bulk_delete_confirm(request: Request) -> Response:
        ids = DepotEleveController._parse_bulk_ids(request)
        if not ids:
            return BaseController.redirect_with_flash(request, "/depot_eleve", "Aucun élément sélectionné.")
        bulk_delete_depot_eleves(ids)
        count = len(ids)
        return BaseController.redirect_with_flash(
            request, "/depot_eleve",
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
        if sort not in {"fichier", "commentaire", "date_depot", "progression_palier_id", "activite_id", "created_at", "updated_at", "id"}:
            sort = ""
        direction = _query_param(request, "direction", "desc")
        if direction not in ("asc", "desc"):
            direction = "asc"
        progression_palier_id_raw = _query_param(request, "progression_palier_id").strip()
        progression_palier_id_f = ""
        if progression_palier_id_raw:
            try:
                progression_palier_id_f = int(progression_palier_id_raw)
            except (TypeError, ValueError):
                progression_palier_id_f = ""
        activite_id_raw = _query_param(request, "activite_id").strip()
        activite_id_f = ""
        if activite_id_raw:
            try:
                activite_id_f = int(activite_id_raw)
            except (TypeError, ValueError):
                activite_id_f = ""
        _filters = {}
        if progression_palier_id_f != "":
            _filters["progression_palier_id"] = progression_palier_id_f
        if activite_id_f != "":
            _filters["activite_id"] = activite_id_f
        rows = find_depot_eleves_for_export(q=q or None, sort=sort or None, direction=direction, filters=_filters or None)
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_ALL)
        writer.writerow([header for header, _ in _CSV_COLS])
        for row in rows:
            writer.writerow([DepotEleveController._csv_escape(str(row.get(key) or "")) for _, key in _CSV_COLS])
        content = output.getvalue().encode("utf-8")
        return Response(
            200,
            content,
            "text/csv; charset=utf-8",
            headers={
                "Content-Disposition": 'attachment; filename="depot_eleves.csv"',
                "Cache-Control": "no-store",
            },
        )
