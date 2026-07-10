import csv
import io
from core.http.request import Request
from core.http.response import Response
from core.mvc.controller import BaseController
from core.mvc.view.pagination import Pagination
from mvc.models.palier_model import (
    get_palier_by_id, add_palier, update_palier, delete_palier, bulk_delete_paliers,
    count_paliers, find_paliers_paginated, find_paliers_for_export,
    get_version_parcours_choices,
)
from mvc.forms.palier_form import PalierForm
from core.security.session import get_flash, get_session_id


def _form_data_from_palier(record: dict) -> dict:
    """Convertit les colonnes SQL vers les noms de champs du formulaire."""
    return {
        "ordre": record.get("Ordre"),
        "titre": record.get("Titre"),
        "theme": record.get("Theme"),
        "production_attendue": record.get("ProductionAttendue"),
        "dossier_technique_fichier": record.get("DossierTechniqueFichier"),
        "version_parcours_id": record.get("version_parcours_id"),
        "created_at": record.get("CreatedAt"),
        "updated_at": record.get("UpdatedAt"),
    }


def _palier_form_options():
    return {
        "version_parcours_id_choices": get_version_parcours_choices(),
    }


def _query_param(request, name, default=""):
    """Retourne le premier paramètre GET, au format parse_qs de Forge."""
    values = request.params.get(name, [default])
    return values[0] if values else default


def _is_hx_request(request):
    """Détecte une requête HTMX locale au CRUD généré."""
    return request.headers.get("HX-Request", "").lower() == "true"


_CSV_COLS = [('Ordre', 'Ordre'), ('Titre', 'Titre'), ('Theme', 'Theme'), ('Production attendue', 'ProductionAttendue'), ('Dossier technique fichier', 'DossierTechniqueFichier'), ('Version parcours id', 'version_parcours_id_label'), ('Created at', 'CreatedAt'), ('Updated at', 'UpdatedAt')]


class PalierController(BaseController):

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
        if sort not in {"ordre", "titre", "theme", "production_attendue", "dossier_technique_fichier", "version_parcours_id", "created_at", "updated_at", "id"}:
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
        relation_filters = {}
        relation_filters["version_parcours_id"] = {"options": [{"id": value, "label": label} for value, label in get_version_parcours_choices()]}
        _filters = {}
        if version_parcours_id_f != "":
            _filters["version_parcours_id"] = version_parcours_id_f
        total    = count_paliers(q or None, filters=_filters or None)
        pagination_state = Pagination(request, total, limit)
        limit = pagination_state.limit
        offset = pagination_state.offset
        empty_context = "search_filters" if q and _filters else ("search" if q else ("filters" if _filters else None))
        paliers = find_paliers_paginated(
            q=q or None, sort=sort or None, direction=direction,
            limit=limit, offset=offset, filters=_filters or None,
        )
        pagination = pagination_state.to_dict()
        pagination.update({
            "q": q, "sort": sort, "direction": direction,
            "filters": {"version_parcours_id": version_parcours_id_f},
        })
        return {
                "paliers": paliers,
                "pagination": pagination,
                "empty_context": empty_context,
                "relation_filters": relation_filters,
                "flash": get_flash(get_session_id(request)),
            }

    @staticmethod
    def index(request: Request) -> Response:
        context = PalierController._list_context(request)
        template = "palier/_results.html" if _is_hx_request(request) else "palier/index.html"
        return BaseController.render(template, context=context, request=request)

    @staticmethod
    def new(request: Request) -> Response:
        form = PalierForm(**_palier_form_options())
        return BaseController.render("palier/form.html",
            context={
                "form": form,
                "action": "/palier/create",
                "titre": "Nouveau palier",
            },
            request=request)

    @staticmethod
    def create(request: Request) -> Response:
        form = PalierForm.from_request(request, **_palier_form_options())
        if not form.is_valid():
            return BaseController.validation_error("palier/form.html",
                context={
                    "form": form,
                    "action": "/palier/create",
                    "titre": "Nouveau palier",
                },
                request=request)
        add_palier(form.cleaned_data)
        return BaseController.redirect_with_flash(request, "/palier", "Palier créé.")

    @staticmethod
    def show(request: Request) -> Response:
        id = PalierController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        palier = get_palier_by_id(id)
        if palier is None:
            return BaseController.not_found()
        return BaseController.render("palier/show.html",
            context={"palier": palier, "flash": get_flash(get_session_id(request))},
            request=request)

    @staticmethod
    def edit(request: Request) -> Response:
        id = PalierController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        palier = get_palier_by_id(id)
        if palier is None:
            return BaseController.not_found()
        return BaseController.render("palier/form.html",
            context={
                "form": PalierForm(_form_data_from_palier(palier), **_palier_form_options()),
                "action": f"/palier/update/{id}",
                "titre": "Modifier palier",
            },
            request=request)

    @staticmethod
    def update(request: Request) -> Response:
        id = PalierController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        form = PalierForm.from_request(request, **_palier_form_options())
        if not form.is_valid():
            return BaseController.validation_error("palier/form.html",
                context={
                    "form": form,
                    "action": f"/palier/update/{id}",
                    "titre": "Modifier palier",
                },
                request=request)
        update_palier(id, form.cleaned_data)
        return BaseController.redirect_with_flash(
            request, f"/palier/show/{id}", "Palier mis à jour.")

    @staticmethod
    def destroy(request: Request) -> Response:
        id = PalierController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        delete_palier(id)
        if _is_hx_request(request):
            context = PalierController._list_context(request)
            return BaseController.render("palier/_results.html", context=context, request=request)
        return BaseController.redirect_with_flash(request, "/palier", "Palier supprimé.")


    @staticmethod
    def bulk_delete(request: Request) -> Response:
        ids = PalierController._parse_bulk_ids(request)
        if not ids:
            return BaseController.redirect_with_flash(request, "/palier", "Aucun élément sélectionné.")
        return BaseController.render("palier/bulk_delete_confirm.html",
            context={"ids": ids, "count": len(ids), "flash": get_flash(get_session_id(request))},
            request=request)

    @staticmethod
    def bulk_delete_confirm(request: Request) -> Response:
        ids = PalierController._parse_bulk_ids(request)
        if not ids:
            return BaseController.redirect_with_flash(request, "/palier", "Aucun élément sélectionné.")
        bulk_delete_paliers(ids)
        count = len(ids)
        return BaseController.redirect_with_flash(
            request, "/palier",
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
        if sort not in {"ordre", "titre", "theme", "production_attendue", "dossier_technique_fichier", "version_parcours_id", "created_at", "updated_at", "id"}:
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
        _filters = {}
        if version_parcours_id_f != "":
            _filters["version_parcours_id"] = version_parcours_id_f
        rows = find_paliers_for_export(q=q or None, sort=sort or None, direction=direction, filters=_filters or None)
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_ALL)
        writer.writerow([header for header, _ in _CSV_COLS])
        for row in rows:
            writer.writerow([PalierController._csv_escape(str(row.get(key) or "")) for _, key in _CSV_COLS])
        content = output.getvalue().encode("utf-8")
        return Response(
            200,
            content,
            "text/csv; charset=utf-8",
            headers={
                "Content-Disposition": 'attachment; filename="paliers.csv"',
                "Cache-Control": "no-store",
            },
        )
