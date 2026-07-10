import csv
import io
from core.http.request import Request
from core.http.response import Response
from core.mvc.controller import BaseController
from core.mvc.view.pagination import Pagination
from mvc.models.progression_eleve_model import (
    get_progression_eleve_by_id, add_progression_eleve, update_progression_eleve, delete_progression_eleve, bulk_delete_progression_eleves,
    count_progression_eleves, find_progression_eleves_paginated, find_progression_eleves_for_export,
    get_eleve_choices, get_affectation_parcours_choices,
)
from mvc.forms.progression_eleve_form import ProgressionEleveForm
from core.security.session import get_flash, get_session_id


def _form_data_from_progression_eleve(record: dict) -> dict:
    """Convertit les colonnes SQL vers les noms de champs du formulaire."""
    return {
        "statut": record.get("Statut"),
        "date_debut": record.get("DateDebut"),
        "eleve_id": record.get("eleve_id"),
        "affectation_parcours_id": record.get("affectation_parcours_id"),
        "created_at": record.get("CreatedAt"),
        "updated_at": record.get("UpdatedAt"),
    }


def _progression_eleve_form_options():
    return {
        "eleve_id_choices": get_eleve_choices(),
        "affectation_parcours_id_choices": get_affectation_parcours_choices(),
    }


def _query_param(request, name, default=""):
    """Retourne le premier paramètre GET, au format parse_qs de Forge."""
    values = request.params.get(name, [default])
    return values[0] if values else default


def _is_hx_request(request):
    """Détecte une requête HTMX locale au CRUD généré."""
    return request.headers.get("HX-Request", "").lower() == "true"


_CSV_COLS = [('Statut', 'Statut'), ('Date debut', 'DateDebut'), ('Eleve id', 'eleve_id_label'), ('Affectation parcours id', 'affectation_parcours_id_label'), ('Created at', 'CreatedAt'), ('Updated at', 'UpdatedAt')]


class ProgressionEleveController(BaseController):

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
        if sort not in {"statut", "date_debut", "eleve_id", "affectation_parcours_id", "created_at", "updated_at", "id"}:
            sort = ""
        direction = _query_param(request, "direction", "desc")
        if direction not in ("asc", "desc"):
            direction = "asc"
        limit  = 20
        eleve_id_raw = _query_param(request, "eleve_id").strip()
        eleve_id_f = ""
        if eleve_id_raw:
            try:
                eleve_id_f = int(eleve_id_raw)
            except (TypeError, ValueError):
                eleve_id_f = ""
        affectation_parcours_id_raw = _query_param(request, "affectation_parcours_id").strip()
        affectation_parcours_id_f = ""
        if affectation_parcours_id_raw:
            try:
                affectation_parcours_id_f = int(affectation_parcours_id_raw)
            except (TypeError, ValueError):
                affectation_parcours_id_f = ""
        relation_filters = {}
        relation_filters["eleve_id"] = {"options": [{"id": value, "label": label} for value, label in get_eleve_choices()]}
        relation_filters["affectation_parcours_id"] = {"options": [{"id": value, "label": label} for value, label in get_affectation_parcours_choices()]}
        _filters = {}
        if eleve_id_f != "":
            _filters["eleve_id"] = eleve_id_f
        if affectation_parcours_id_f != "":
            _filters["affectation_parcours_id"] = affectation_parcours_id_f
        total    = count_progression_eleves(q or None, filters=_filters or None)
        pagination_state = Pagination(request, total, limit)
        limit = pagination_state.limit
        offset = pagination_state.offset
        empty_context = "search_filters" if q and _filters else ("search" if q else ("filters" if _filters else None))
        progression_eleves = find_progression_eleves_paginated(
            q=q or None, sort=sort or None, direction=direction,
            limit=limit, offset=offset, filters=_filters or None,
        )
        pagination = pagination_state.to_dict()
        pagination.update({
            "q": q, "sort": sort, "direction": direction,
            "filters": {"eleve_id": eleve_id_f, "affectation_parcours_id": affectation_parcours_id_f},
        })
        return {
                "progression_eleves": progression_eleves,
                "pagination": pagination,
                "empty_context": empty_context,
                "relation_filters": relation_filters,
                "flash": get_flash(get_session_id(request)),
            }

    @staticmethod
    def index(request: Request) -> Response:
        context = ProgressionEleveController._list_context(request)
        template = "progression_eleve/_results.html" if _is_hx_request(request) else "progression_eleve/index.html"
        return BaseController.render(template, context=context, request=request)

    @staticmethod
    def new(request: Request) -> Response:
        form = ProgressionEleveForm(**_progression_eleve_form_options())
        return BaseController.render("progression_eleve/form.html",
            context={
                "form": form,
                "action": "/progression_eleve/create",
                "titre": "Nouveau progression_eleve",
            },
            request=request)

    @staticmethod
    def create(request: Request) -> Response:
        form = ProgressionEleveForm.from_request(request, **_progression_eleve_form_options())
        if not form.is_valid():
            return BaseController.validation_error("progression_eleve/form.html",
                context={
                    "form": form,
                    "action": "/progression_eleve/create",
                    "titre": "Nouveau progression_eleve",
                },
                request=request)
        add_progression_eleve(form.cleaned_data)
        return BaseController.redirect_with_flash(request, "/progression_eleve", "ProgressionEleve créé.")

    @staticmethod
    def show(request: Request) -> Response:
        id = ProgressionEleveController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        progression_eleve = get_progression_eleve_by_id(id)
        if progression_eleve is None:
            return BaseController.not_found()
        return BaseController.render("progression_eleve/show.html",
            context={"progression_eleve": progression_eleve, "flash": get_flash(get_session_id(request))},
            request=request)

    @staticmethod
    def edit(request: Request) -> Response:
        id = ProgressionEleveController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        progression_eleve = get_progression_eleve_by_id(id)
        if progression_eleve is None:
            return BaseController.not_found()
        return BaseController.render("progression_eleve/form.html",
            context={
                "form": ProgressionEleveForm(_form_data_from_progression_eleve(progression_eleve), **_progression_eleve_form_options()),
                "action": f"/progression_eleve/update/{id}",
                "titre": "Modifier progression_eleve",
            },
            request=request)

    @staticmethod
    def update(request: Request) -> Response:
        id = ProgressionEleveController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        form = ProgressionEleveForm.from_request(request, **_progression_eleve_form_options())
        if not form.is_valid():
            return BaseController.validation_error("progression_eleve/form.html",
                context={
                    "form": form,
                    "action": f"/progression_eleve/update/{id}",
                    "titre": "Modifier progression_eleve",
                },
                request=request)
        update_progression_eleve(id, form.cleaned_data)
        return BaseController.redirect_with_flash(
            request, f"/progression_eleve/show/{id}", "ProgressionEleve mis à jour.")

    @staticmethod
    def destroy(request: Request) -> Response:
        id = ProgressionEleveController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        delete_progression_eleve(id)
        if _is_hx_request(request):
            context = ProgressionEleveController._list_context(request)
            return BaseController.render("progression_eleve/_results.html", context=context, request=request)
        return BaseController.redirect_with_flash(request, "/progression_eleve", "ProgressionEleve supprimé.")


    @staticmethod
    def bulk_delete(request: Request) -> Response:
        ids = ProgressionEleveController._parse_bulk_ids(request)
        if not ids:
            return BaseController.redirect_with_flash(request, "/progression_eleve", "Aucun élément sélectionné.")
        return BaseController.render("progression_eleve/bulk_delete_confirm.html",
            context={"ids": ids, "count": len(ids), "flash": get_flash(get_session_id(request))},
            request=request)

    @staticmethod
    def bulk_delete_confirm(request: Request) -> Response:
        ids = ProgressionEleveController._parse_bulk_ids(request)
        if not ids:
            return BaseController.redirect_with_flash(request, "/progression_eleve", "Aucun élément sélectionné.")
        bulk_delete_progression_eleves(ids)
        count = len(ids)
        return BaseController.redirect_with_flash(
            request, "/progression_eleve",
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
        if sort not in {"statut", "date_debut", "eleve_id", "affectation_parcours_id", "created_at", "updated_at", "id"}:
            sort = ""
        direction = _query_param(request, "direction", "desc")
        if direction not in ("asc", "desc"):
            direction = "asc"
        eleve_id_raw = _query_param(request, "eleve_id").strip()
        eleve_id_f = ""
        if eleve_id_raw:
            try:
                eleve_id_f = int(eleve_id_raw)
            except (TypeError, ValueError):
                eleve_id_f = ""
        affectation_parcours_id_raw = _query_param(request, "affectation_parcours_id").strip()
        affectation_parcours_id_f = ""
        if affectation_parcours_id_raw:
            try:
                affectation_parcours_id_f = int(affectation_parcours_id_raw)
            except (TypeError, ValueError):
                affectation_parcours_id_f = ""
        _filters = {}
        if eleve_id_f != "":
            _filters["eleve_id"] = eleve_id_f
        if affectation_parcours_id_f != "":
            _filters["affectation_parcours_id"] = affectation_parcours_id_f
        rows = find_progression_eleves_for_export(q=q or None, sort=sort or None, direction=direction, filters=_filters or None)
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_ALL)
        writer.writerow([header for header, _ in _CSV_COLS])
        for row in rows:
            writer.writerow([ProgressionEleveController._csv_escape(str(row.get(key) or "")) for _, key in _CSV_COLS])
        content = output.getvalue().encode("utf-8")
        return Response(
            200,
            content,
            "text/csv; charset=utf-8",
            headers={
                "Content-Disposition": 'attachment; filename="progression_eleves.csv"',
                "Cache-Control": "no-store",
            },
        )
