import csv
import io
from core.http.request import Request
from core.http.response import Response
from core.mvc.controller import BaseController
from core.mvc.view.pagination import Pagination
from mvc.models.affectation_parcours_model import (
    get_affectation_parcours_by_id, add_affectation_parcours, update_affectation_parcours, delete_affectation_parcours, bulk_delete_affectation_parcourss,
    count_affectation_parcourss, find_affectation_parcourss_paginated, find_affectation_parcourss_for_export,
    get_version_parcours_choices, get_classe_choices, get_professeur_choices, get_eleve_choices,
    get_affectation_parcours_eleve_ids, add_affectation_parcours_eleve_ids, sync_affectation_parcours_eleve_ids, get_affectation_parcours_eleve_labels_by_affectation_parcours_id, get_affectation_parcours_eleve_labels,
)
from mvc.forms.affectation_parcours_form import AffectationParcoursForm
from core.security.session import get_flash, get_session_id


def _form_data_from_affectation_parcours(record: dict) -> dict:
    """Convertit les colonnes SQL vers les noms de champs du formulaire."""
    return {
        "date_affectation": record.get("DateAffectation"),
        "statut": record.get("Statut"),
        "version_parcours_id": record.get("version_parcours_id"),
        "classe_id": record.get("classe_id"),
        "professeur_id": record.get("professeur_id"),
        "created_at": record.get("CreatedAt"),
        "updated_at": record.get("UpdatedAt"),
    }


def _affectation_parcours_form_options():
    return {
        "version_parcours_id_choices": get_version_parcours_choices(),
        "classe_id_choices": get_classe_choices(),
        "professeur_id_choices": get_professeur_choices(),
    }


def _query_param(request, name, default=""):
    """Retourne le premier paramètre GET, au format parse_qs de Forge."""
    values = request.params.get(name, [default])
    return values[0] if values else default


def _is_hx_request(request):
    """Détecte une requête HTMX locale au CRUD généré."""
    return request.headers.get("HX-Request", "").lower() == "true"


_CSV_COLS = [('Date affectation', 'DateAffectation'), ('Statut', 'Statut'), ('Version parcours id', 'version_parcours_id_label'), ('Classe id', 'classe_id_label'), ('Professeur id', 'professeur_id_label'), ('Created at', 'CreatedAt'), ('Updated at', 'UpdatedAt')]


class AffectationParcoursController(BaseController):

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
        if sort not in {"date_affectation", "statut", "version_parcours_id", "classe_id", "professeur_id", "created_at", "updated_at", "id"}:
            sort = ""
        direction = _query_param(request, "direction", "desc")
        if direction not in ("asc", "desc"):
            direction = "asc"
        limit  = 20
        version_parcours_id_raw = _query_param(request, "version_parcours_id").strip()
        version_parcours_id_f = ""
        if version_parcours_id_raw:
            try:
                version_parcours_id_f = int(version_parcours_id_raw)
            except (TypeError, ValueError):
                version_parcours_id_f = ""
        classe_id_raw = _query_param(request, "classe_id").strip()
        classe_id_f = ""
        if classe_id_raw:
            try:
                classe_id_f = int(classe_id_raw)
            except (TypeError, ValueError):
                classe_id_f = ""
        professeur_id_raw = _query_param(request, "professeur_id").strip()
        professeur_id_f = ""
        if professeur_id_raw:
            try:
                professeur_id_f = int(professeur_id_raw)
            except (TypeError, ValueError):
                professeur_id_f = ""
        relation_filters = {}
        relation_filters["version_parcours_id"] = {"options": [{"id": value, "label": label} for value, label in get_version_parcours_choices()]}
        relation_filters["classe_id"] = {"options": [{"id": value, "label": label} for value, label in get_classe_choices()]}
        relation_filters["professeur_id"] = {"options": [{"id": value, "label": label} for value, label in get_professeur_choices()]}
        _filters = {}
        if version_parcours_id_f != "":
            _filters["version_parcours_id"] = version_parcours_id_f
        if classe_id_f != "":
            _filters["classe_id"] = classe_id_f
        if professeur_id_f != "":
            _filters["professeur_id"] = professeur_id_f
        total    = count_affectation_parcourss(q or None, filters=_filters or None)
        pagination_state = Pagination(request, total, limit)
        limit = pagination_state.limit
        offset = pagination_state.offset
        empty_context = "search_filters" if q and _filters else ("search" if q else ("filters" if _filters else None))
        affectation_parcourss = find_affectation_parcourss_paginated(
            q=q or None, sort=sort or None, direction=direction,
            limit=limit, offset=offset, filters=_filters or None,
        )
        pagination = pagination_state.to_dict()
        pagination.update({
            "q": q, "sort": sort, "direction": direction,
            "filters": {"version_parcours_id": version_parcours_id_f, "classe_id": classe_id_f, "professeur_id": professeur_id_f},
        })
        return {
                "affectation_parcourss": affectation_parcourss,
                "pagination": pagination,
                "empty_context": empty_context,
                "relation_filters": relation_filters,
                "flash": get_flash(get_session_id(request)),
                "eleves_by_affectation_parcours_id": get_affectation_parcours_eleve_labels_by_affectation_parcours_id([row["Id"] for row in affectation_parcourss]),
            }

    @staticmethod
    def index(request: Request) -> Response:
        context = AffectationParcoursController._list_context(request)
        template = "affectation_parcours/_results.html" if _is_hx_request(request) else "affectation_parcours/index.html"
        return BaseController.render(template, context=context, request=request)

    @staticmethod
    def new(request: Request) -> Response:
        form = AffectationParcoursForm(**_affectation_parcours_form_options())
        return BaseController.render("affectation_parcours/form.html",
            context={
                "form": form,
                "action": "/affectation_parcours/create",
                "titre": "Nouveau affectation_parcours",
                "eleve_choices": get_eleve_choices(),
                "eleve_ids_selected": [],
            },
            request=request)

    @staticmethod
    def create(request: Request) -> Response:
        form = AffectationParcoursForm.from_request(request, **_affectation_parcours_form_options())
        eleve_ids = AffectationParcoursController._parse_many_ids(request, "eleve_ids")
        if not form.is_valid():
            return BaseController.validation_error("affectation_parcours/form.html",
                context={
                    "form": form,
                    "action": "/affectation_parcours/create",
                    "titre": "Nouveau affectation_parcours",
                    "eleve_choices": get_eleve_choices(),
                    "eleve_ids_selected": eleve_ids,
                },
                request=request)
        created_id = add_affectation_parcours(form.cleaned_data)
        add_affectation_parcours_eleve_ids(created_id, eleve_ids)
        return BaseController.redirect_with_flash(request, "/affectation_parcours", "AffectationParcours créé.")

    @staticmethod
    def show(request: Request) -> Response:
        id = AffectationParcoursController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        affectation_parcours = get_affectation_parcours_by_id(id)
        if affectation_parcours is None:
            return BaseController.not_found()
        eleve_labels = get_affectation_parcours_eleve_labels(id)
        return BaseController.render("affectation_parcours/show.html",
            context={"affectation_parcours": affectation_parcours, "flash": get_flash(get_session_id(request)), "eleve_labels": eleve_labels},
            request=request)

    @staticmethod
    def edit(request: Request) -> Response:
        id = AffectationParcoursController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        affectation_parcours = get_affectation_parcours_by_id(id)
        if affectation_parcours is None:
            return BaseController.not_found()
        return BaseController.render("affectation_parcours/form.html",
            context={
                "form": AffectationParcoursForm(_form_data_from_affectation_parcours(affectation_parcours), **_affectation_parcours_form_options()),
                "action": f"/affectation_parcours/update/{id}",
                "titre": "Modifier affectation_parcours",
                "eleve_choices": get_eleve_choices(),
                "eleve_ids_selected": get_affectation_parcours_eleve_ids(id),
            },
            request=request)

    @staticmethod
    def update(request: Request) -> Response:
        id = AffectationParcoursController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        form = AffectationParcoursForm.from_request(request, **_affectation_parcours_form_options())
        eleve_ids = AffectationParcoursController._parse_many_ids(request, "eleve_ids")
        if not form.is_valid():
            return BaseController.validation_error("affectation_parcours/form.html",
                context={
                    "form": form,
                    "action": f"/affectation_parcours/update/{id}",
                    "titre": "Modifier affectation_parcours",
                    "eleve_choices": get_eleve_choices(),
                    "eleve_ids_selected": eleve_ids,
                },
                request=request)
        update_affectation_parcours(id, form.cleaned_data)
        sync_affectation_parcours_eleve_ids(id, eleve_ids)
        return BaseController.redirect_with_flash(
            request, f"/affectation_parcours/show/{id}", "AffectationParcours mis à jour.")

    @staticmethod
    def destroy(request: Request) -> Response:
        id = AffectationParcoursController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        delete_affectation_parcours(id)
        if _is_hx_request(request):
            context = AffectationParcoursController._list_context(request)
            return BaseController.render("affectation_parcours/_results.html", context=context, request=request)
        return BaseController.redirect_with_flash(request, "/affectation_parcours", "AffectationParcours supprimé.")


    @staticmethod
    def bulk_delete(request: Request) -> Response:
        ids = AffectationParcoursController._parse_bulk_ids(request)
        if not ids:
            return BaseController.redirect_with_flash(request, "/affectation_parcours", "Aucun élément sélectionné.")
        return BaseController.render("affectation_parcours/bulk_delete_confirm.html",
            context={"ids": ids, "count": len(ids), "flash": get_flash(get_session_id(request))},
            request=request)

    @staticmethod
    def bulk_delete_confirm(request: Request) -> Response:
        ids = AffectationParcoursController._parse_bulk_ids(request)
        if not ids:
            return BaseController.redirect_with_flash(request, "/affectation_parcours", "Aucun élément sélectionné.")
        bulk_delete_affectation_parcourss(ids)
        count = len(ids)
        return BaseController.redirect_with_flash(
            request, "/affectation_parcours",
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
        if sort not in {"date_affectation", "statut", "version_parcours_id", "classe_id", "professeur_id", "created_at", "updated_at", "id"}:
            sort = ""
        direction = _query_param(request, "direction", "desc")
        if direction not in ("asc", "desc"):
            direction = "asc"
        version_parcours_id_raw = _query_param(request, "version_parcours_id").strip()
        version_parcours_id_f = ""
        if version_parcours_id_raw:
            try:
                version_parcours_id_f = int(version_parcours_id_raw)
            except (TypeError, ValueError):
                version_parcours_id_f = ""
        classe_id_raw = _query_param(request, "classe_id").strip()
        classe_id_f = ""
        if classe_id_raw:
            try:
                classe_id_f = int(classe_id_raw)
            except (TypeError, ValueError):
                classe_id_f = ""
        professeur_id_raw = _query_param(request, "professeur_id").strip()
        professeur_id_f = ""
        if professeur_id_raw:
            try:
                professeur_id_f = int(professeur_id_raw)
            except (TypeError, ValueError):
                professeur_id_f = ""
        _filters = {}
        if version_parcours_id_f != "":
            _filters["version_parcours_id"] = version_parcours_id_f
        if classe_id_f != "":
            _filters["classe_id"] = classe_id_f
        if professeur_id_f != "":
            _filters["professeur_id"] = professeur_id_f
        rows = find_affectation_parcourss_for_export(q=q or None, sort=sort or None, direction=direction, filters=_filters or None)
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_ALL)
        writer.writerow([header for header, _ in _CSV_COLS])
        for row in rows:
            writer.writerow([AffectationParcoursController._csv_escape(str(row.get(key) or "")) for _, key in _CSV_COLS])
        content = output.getvalue().encode("utf-8")
        return Response(
            200,
            content,
            "text/csv; charset=utf-8",
            headers={
                "Content-Disposition": 'attachment; filename="affectation_parcourss.csv"',
                "Cache-Control": "no-store",
            },
        )
