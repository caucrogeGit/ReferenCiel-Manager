import csv
import io
from core.http.request import Request
from core.http.response import Response
from core.mvc.controller import BaseController
from core.mvc.view.pagination import Pagination
from mvc.models.classe_model import (
    get_classe_by_id, add_classe, update_classe, delete_classe, bulk_delete_classes,
    count_classes, find_classes_paginated, find_classes_for_export,
    get_annee_scolaire_choices, get_niveau_classe_choices,
)
from mvc.forms.classe_form import ClasseForm
from core.security.session import get_flash, get_session_id


def _form_data_from_classe(record: dict) -> dict:
    """Convertit les colonnes SQL vers les noms de champs du formulaire."""
    return {
        "code": record.get("Code"),
        "libelle": record.get("Libelle"),
        "created_at": record.get("CreatedAt"),
        "updated_at": record.get("UpdatedAt"),
        "annee_scolaire_id": record.get("annee_scolaire_id"),
        "niveau_classe_id": record.get("niveau_classe_id"),
    }


def _classe_form_options():
    return {
        "annee_scolaire_id_choices": get_annee_scolaire_choices(),
        "niveau_classe_id_choices": get_niveau_classe_choices(),
    }


def _query_param(request, name, default=""):
    """Retourne le premier paramètre GET, au format parse_qs de Forge."""
    values = request.params.get(name, [default])
    return values[0] if values else default


def _is_hx_request(request):
    """Détecte une requête HTMX locale au CRUD généré."""
    return request.headers.get("HX-Request", "").lower() == "true"


_CSV_COLS = [('Code', 'Code'), ('Libelle', 'Libelle'), ('Created at', 'CreatedAt'), ('Updated at', 'UpdatedAt'), ('Annee scolaire id', 'annee_scolaire_id_label'), ('Niveau classe id', 'niveau_classe_id_label')]


class ClasseController(BaseController):

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
        if sort not in {"code", "libelle", "created_at", "updated_at", "annee_scolaire_id", "niveau_classe_id", "id"}:
            sort = ""
        direction = _query_param(request, "direction", "desc")
        if direction not in ("asc", "desc"):
            direction = "asc"
        limit  = 20
        annee_scolaire_id_raw = _query_param(request, "annee_scolaire_id").strip()
        annee_scolaire_id_f = ""
        if annee_scolaire_id_raw:
            try:
                annee_scolaire_id_f = int(annee_scolaire_id_raw)
            except (TypeError, ValueError):
                annee_scolaire_id_f = ""
        niveau_classe_id_raw = _query_param(request, "niveau_classe_id").strip()
        niveau_classe_id_f = ""
        if niveau_classe_id_raw:
            try:
                niveau_classe_id_f = int(niveau_classe_id_raw)
            except (TypeError, ValueError):
                niveau_classe_id_f = ""
        relation_filters = {}
        relation_filters["annee_scolaire_id"] = {"options": [{"id": value, "label": label} for value, label in get_annee_scolaire_choices()]}
        relation_filters["niveau_classe_id"] = {"options": [{"id": value, "label": label} for value, label in get_niveau_classe_choices()]}
        _filters = {}
        if annee_scolaire_id_f != "":
            _filters["annee_scolaire_id"] = annee_scolaire_id_f
        if niveau_classe_id_f != "":
            _filters["niveau_classe_id"] = niveau_classe_id_f
        total    = count_classes(q or None, filters=_filters or None)
        pagination_state = Pagination(request, total, limit)
        limit = pagination_state.limit
        offset = pagination_state.offset
        empty_context = "search_filters" if q and _filters else ("search" if q else ("filters" if _filters else None))
        classes = find_classes_paginated(
            q=q or None, sort=sort or None, direction=direction,
            limit=limit, offset=offset, filters=_filters or None,
        )
        pagination = pagination_state.to_dict()
        pagination.update({
            "q": q, "sort": sort, "direction": direction,
            "filters": {"annee_scolaire_id": annee_scolaire_id_f, "niveau_classe_id": niveau_classe_id_f},
        })
        return {
                "classes": classes,
                "pagination": pagination,
                "empty_context": empty_context,
                "relation_filters": relation_filters,
                "flash": get_flash(get_session_id(request)),
            }

    @staticmethod
    def index(request: Request) -> Response:
        context = ClasseController._list_context(request)
        template = "classe/_results.html" if _is_hx_request(request) else "classe/index.html"
        return BaseController.render(template, context=context, request=request)

    @staticmethod
    def new(request: Request) -> Response:
        form = ClasseForm(**_classe_form_options())
        return BaseController.render("classe/form.html",
            context={
                "form": form,
                "action": "/classe/create",
                "titre": "Nouveau classe",
            },
            request=request)

    @staticmethod
    def create(request: Request) -> Response:
        form = ClasseForm.from_request(request, **_classe_form_options())
        if not form.is_valid():
            return BaseController.validation_error("classe/form.html",
                context={
                    "form": form,
                    "action": "/classe/create",
                    "titre": "Nouveau classe",
                },
                request=request)
        add_classe(form.cleaned_data)
        return BaseController.redirect_with_flash(request, "/classe", "Classe créé.")

    @staticmethod
    def show(request: Request) -> Response:
        id = ClasseController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        classe = get_classe_by_id(id)
        if classe is None:
            return BaseController.not_found()
        return BaseController.render("classe/show.html",
            context={"classe": classe, "flash": get_flash(get_session_id(request))},
            request=request)

    @staticmethod
    def edit(request: Request) -> Response:
        id = ClasseController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        classe = get_classe_by_id(id)
        if classe is None:
            return BaseController.not_found()
        return BaseController.render("classe/form.html",
            context={
                "form": ClasseForm(_form_data_from_classe(classe), **_classe_form_options()),
                "action": f"/classe/update/{id}",
                "titre": "Modifier classe",
            },
            request=request)

    @staticmethod
    def update(request: Request) -> Response:
        id = ClasseController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        form = ClasseForm.from_request(request, **_classe_form_options())
        if not form.is_valid():
            return BaseController.validation_error("classe/form.html",
                context={
                    "form": form,
                    "action": f"/classe/update/{id}",
                    "titre": "Modifier classe",
                },
                request=request)
        update_classe(id, form.cleaned_data)
        return BaseController.redirect_with_flash(
            request, f"/classe/show/{id}", "Classe mis à jour.")

    @staticmethod
    def destroy(request: Request) -> Response:
        id = ClasseController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        delete_classe(id)
        if _is_hx_request(request):
            context = ClasseController._list_context(request)
            return BaseController.render("classe/_results.html", context=context, request=request)
        return BaseController.redirect_with_flash(request, "/classe", "Classe supprimé.")


    @staticmethod
    def bulk_delete(request: Request) -> Response:
        ids = ClasseController._parse_bulk_ids(request)
        if not ids:
            return BaseController.redirect_with_flash(request, "/classe", "Aucun élément sélectionné.")
        return BaseController.render("classe/bulk_delete_confirm.html",
            context={"ids": ids, "count": len(ids), "flash": get_flash(get_session_id(request))},
            request=request)

    @staticmethod
    def bulk_delete_confirm(request: Request) -> Response:
        ids = ClasseController._parse_bulk_ids(request)
        if not ids:
            return BaseController.redirect_with_flash(request, "/classe", "Aucun élément sélectionné.")
        bulk_delete_classes(ids)
        count = len(ids)
        return BaseController.redirect_with_flash(
            request, "/classe",
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
        if sort not in {"code", "libelle", "created_at", "updated_at", "annee_scolaire_id", "niveau_classe_id", "id"}:
            sort = ""
        direction = _query_param(request, "direction", "desc")
        if direction not in ("asc", "desc"):
            direction = "asc"
        annee_scolaire_id_raw = _query_param(request, "annee_scolaire_id").strip()
        annee_scolaire_id_f = ""
        if annee_scolaire_id_raw:
            try:
                annee_scolaire_id_f = int(annee_scolaire_id_raw)
            except (TypeError, ValueError):
                annee_scolaire_id_f = ""
        niveau_classe_id_raw = _query_param(request, "niveau_classe_id").strip()
        niveau_classe_id_f = ""
        if niveau_classe_id_raw:
            try:
                niveau_classe_id_f = int(niveau_classe_id_raw)
            except (TypeError, ValueError):
                niveau_classe_id_f = ""
        _filters = {}
        if annee_scolaire_id_f != "":
            _filters["annee_scolaire_id"] = annee_scolaire_id_f
        if niveau_classe_id_f != "":
            _filters["niveau_classe_id"] = niveau_classe_id_f
        rows = find_classes_for_export(q=q or None, sort=sort or None, direction=direction, filters=_filters or None)
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_ALL)
        writer.writerow([header for header, _ in _CSV_COLS])
        for row in rows:
            writer.writerow([ClasseController._csv_escape(str(row.get(key) or "")) for _, key in _CSV_COLS])
        content = output.getvalue().encode("utf-8")
        return Response(
            200,
            content,
            "text/csv; charset=utf-8",
            headers={
                "Content-Disposition": 'attachment; filename="classes.csv"',
                "Cache-Control": "no-store",
            },
        )
