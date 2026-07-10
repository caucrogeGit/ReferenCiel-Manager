import csv
import io
from core.http.request import Request
from core.http.response import Response
from core.mvc.controller import BaseController
from core.mvc.view.pagination import Pagination
from mvc.models.affectation_professeur_classe_model import (
    get_affectation_professeur_classe_by_id, add_affectation_professeur_classe, update_affectation_professeur_classe, delete_affectation_professeur_classe, bulk_delete_affectation_professeur_classes,
    count_affectation_professeur_classes, find_affectation_professeur_classes_paginated, find_affectation_professeur_classes_for_export,
    get_professeur_choices, get_classe_choices, get_annee_scolaire_choices,
)
from mvc.forms.affectation_professeur_classe_form import AffectationProfesseurClasseForm
from core.security.session import get_flash, get_session_id


def _form_data_from_affectation_professeur_classe(record: dict) -> dict:
    """Convertit les colonnes SQL vers les noms de champs du formulaire."""
    return {
        "role": record.get("Role"),
        "professeur_id": record.get("professeur_id"),
        "classe_id": record.get("classe_id"),
        "annee_scolaire_id": record.get("annee_scolaire_id"),
        "created_at": record.get("CreatedAt"),
        "updated_at": record.get("UpdatedAt"),
    }


def _affectation_professeur_classe_form_options():
    return {
        "professeur_id_choices": get_professeur_choices(),
        "classe_id_choices": get_classe_choices(),
        "annee_scolaire_id_choices": get_annee_scolaire_choices(),
    }


def _query_param(request, name, default=""):
    """Retourne le premier paramètre GET, au format parse_qs de Forge."""
    values = request.params.get(name, [default])
    return values[0] if values else default


def _is_hx_request(request):
    """Détecte une requête HTMX locale au CRUD généré."""
    return request.headers.get("HX-Request", "").lower() == "true"


_CSV_COLS = [('Role', 'Role'), ('Professeur id', 'professeur_id_label'), ('Classe id', 'classe_id_label'), ('Annee scolaire id', 'annee_scolaire_id_label'), ('Created at', 'CreatedAt'), ('Updated at', 'UpdatedAt')]


class AffectationProfesseurClasseController(BaseController):

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
        if sort not in {"role", "professeur_id", "classe_id", "annee_scolaire_id", "created_at", "updated_at", "id"}:
            sort = ""
        direction = _query_param(request, "direction", "desc")
        if direction not in ("asc", "desc"):
            direction = "asc"
        limit  = 20
        professeur_id_raw = _query_param(request, "professeur_id").strip()
        professeur_id_f = ""
        if professeur_id_raw:
            try:
                professeur_id_f = int(professeur_id_raw)
            except (TypeError, ValueError):
                professeur_id_f = ""
        classe_id_raw = _query_param(request, "classe_id").strip()
        classe_id_f = ""
        if classe_id_raw:
            try:
                classe_id_f = int(classe_id_raw)
            except (TypeError, ValueError):
                classe_id_f = ""
        annee_scolaire_id_raw = _query_param(request, "annee_scolaire_id").strip()
        annee_scolaire_id_f = ""
        if annee_scolaire_id_raw:
            try:
                annee_scolaire_id_f = int(annee_scolaire_id_raw)
            except (TypeError, ValueError):
                annee_scolaire_id_f = ""
        relation_filters = {}
        relation_filters["professeur_id"] = {"options": [{"id": value, "label": label} for value, label in get_professeur_choices()]}
        relation_filters["classe_id"] = {"options": [{"id": value, "label": label} for value, label in get_classe_choices()]}
        relation_filters["annee_scolaire_id"] = {"options": [{"id": value, "label": label} for value, label in get_annee_scolaire_choices()]}
        _filters = {}
        if professeur_id_f != "":
            _filters["professeur_id"] = professeur_id_f
        if classe_id_f != "":
            _filters["classe_id"] = classe_id_f
        if annee_scolaire_id_f != "":
            _filters["annee_scolaire_id"] = annee_scolaire_id_f
        total    = count_affectation_professeur_classes(q or None, filters=_filters or None)
        pagination_state = Pagination(request, total, limit)
        limit = pagination_state.limit
        offset = pagination_state.offset
        empty_context = "search_filters" if q and _filters else ("search" if q else ("filters" if _filters else None))
        affectation_professeur_classes = find_affectation_professeur_classes_paginated(
            q=q or None, sort=sort or None, direction=direction,
            limit=limit, offset=offset, filters=_filters or None,
        )
        pagination = pagination_state.to_dict()
        pagination.update({
            "q": q, "sort": sort, "direction": direction,
            "filters": {"professeur_id": professeur_id_f, "classe_id": classe_id_f, "annee_scolaire_id": annee_scolaire_id_f},
        })
        return {
                "affectation_professeur_classes": affectation_professeur_classes,
                "pagination": pagination,
                "empty_context": empty_context,
                "relation_filters": relation_filters,
                "flash": get_flash(get_session_id(request)),
            }

    @staticmethod
    def index(request: Request) -> Response:
        context = AffectationProfesseurClasseController._list_context(request)
        template = "app/affectation_professeur_classe/_results.html" if _is_hx_request(request) else "app/affectation_professeur_classe/index.html"
        return BaseController.render(template, context=context, request=request)

    @staticmethod
    def new(request: Request) -> Response:
        form = AffectationProfesseurClasseForm(**_affectation_professeur_classe_form_options())
        return BaseController.render("app/affectation_professeur_classe/form.html",
            context={
                "form": form,
                "action": "/affectation_professeur_classe/create",
                "titre": "Nouveau affectation_professeur_classe",
            },
            request=request)

    @staticmethod
    def create(request: Request) -> Response:
        form = AffectationProfesseurClasseForm.from_request(request, **_affectation_professeur_classe_form_options())
        if not form.is_valid():
            return BaseController.validation_error("app/affectation_professeur_classe/form.html",
                context={
                    "form": form,
                    "action": "/affectation_professeur_classe/create",
                    "titre": "Nouveau affectation_professeur_classe",
                },
                request=request)
        add_affectation_professeur_classe(form.cleaned_data)
        return BaseController.redirect_with_flash(request, "/affectation_professeur_classe", "AffectationProfesseurClasse créé.")

    @staticmethod
    def show(request: Request) -> Response:
        id = AffectationProfesseurClasseController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        affectation_professeur_classe = get_affectation_professeur_classe_by_id(id)
        if affectation_professeur_classe is None:
            return BaseController.not_found()
        return BaseController.render("app/affectation_professeur_classe/show.html",
            context={"affectation_professeur_classe": affectation_professeur_classe, "flash": get_flash(get_session_id(request))},
            request=request)

    @staticmethod
    def edit(request: Request) -> Response:
        id = AffectationProfesseurClasseController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        affectation_professeur_classe = get_affectation_professeur_classe_by_id(id)
        if affectation_professeur_classe is None:
            return BaseController.not_found()
        return BaseController.render("app/affectation_professeur_classe/form.html",
            context={
                "form": AffectationProfesseurClasseForm(_form_data_from_affectation_professeur_classe(affectation_professeur_classe), **_affectation_professeur_classe_form_options()),
                "action": f"/affectation_professeur_classe/update/{id}",
                "titre": "Modifier affectation_professeur_classe",
            },
            request=request)

    @staticmethod
    def update(request: Request) -> Response:
        id = AffectationProfesseurClasseController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        form = AffectationProfesseurClasseForm.from_request(request, **_affectation_professeur_classe_form_options())
        if not form.is_valid():
            return BaseController.validation_error("app/affectation_professeur_classe/form.html",
                context={
                    "form": form,
                    "action": f"/affectation_professeur_classe/update/{id}",
                    "titre": "Modifier affectation_professeur_classe",
                },
                request=request)
        update_affectation_professeur_classe(id, form.cleaned_data)
        return BaseController.redirect_with_flash(
            request, f"/affectation_professeur_classe/show/{id}", "AffectationProfesseurClasse mis à jour.")

    @staticmethod
    def destroy(request: Request) -> Response:
        id = AffectationProfesseurClasseController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        delete_affectation_professeur_classe(id)
        if _is_hx_request(request):
            context = AffectationProfesseurClasseController._list_context(request)
            return BaseController.render("app/affectation_professeur_classe/_results.html", context=context, request=request)
        return BaseController.redirect_with_flash(request, "/affectation_professeur_classe", "AffectationProfesseurClasse supprimé.")


    @staticmethod
    def bulk_delete(request: Request) -> Response:
        ids = AffectationProfesseurClasseController._parse_bulk_ids(request)
        if not ids:
            return BaseController.redirect_with_flash(request, "/affectation_professeur_classe", "Aucun élément sélectionné.")
        return BaseController.render("app/affectation_professeur_classe/bulk_delete_confirm.html",
            context={"ids": ids, "count": len(ids), "flash": get_flash(get_session_id(request))},
            request=request)

    @staticmethod
    def bulk_delete_confirm(request: Request) -> Response:
        ids = AffectationProfesseurClasseController._parse_bulk_ids(request)
        if not ids:
            return BaseController.redirect_with_flash(request, "/affectation_professeur_classe", "Aucun élément sélectionné.")
        bulk_delete_affectation_professeur_classes(ids)
        count = len(ids)
        return BaseController.redirect_with_flash(
            request, "/affectation_professeur_classe",
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
        if sort not in {"role", "professeur_id", "classe_id", "annee_scolaire_id", "created_at", "updated_at", "id"}:
            sort = ""
        direction = _query_param(request, "direction", "desc")
        if direction not in ("asc", "desc"):
            direction = "asc"
        professeur_id_raw = _query_param(request, "professeur_id").strip()
        professeur_id_f = ""
        if professeur_id_raw:
            try:
                professeur_id_f = int(professeur_id_raw)
            except (TypeError, ValueError):
                professeur_id_f = ""
        classe_id_raw = _query_param(request, "classe_id").strip()
        classe_id_f = ""
        if classe_id_raw:
            try:
                classe_id_f = int(classe_id_raw)
            except (TypeError, ValueError):
                classe_id_f = ""
        annee_scolaire_id_raw = _query_param(request, "annee_scolaire_id").strip()
        annee_scolaire_id_f = ""
        if annee_scolaire_id_raw:
            try:
                annee_scolaire_id_f = int(annee_scolaire_id_raw)
            except (TypeError, ValueError):
                annee_scolaire_id_f = ""
        _filters = {}
        if professeur_id_f != "":
            _filters["professeur_id"] = professeur_id_f
        if classe_id_f != "":
            _filters["classe_id"] = classe_id_f
        if annee_scolaire_id_f != "":
            _filters["annee_scolaire_id"] = annee_scolaire_id_f
        rows = find_affectation_professeur_classes_for_export(q=q or None, sort=sort or None, direction=direction, filters=_filters or None)
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_ALL)
        writer.writerow([header for header, _ in _CSV_COLS])
        for row in rows:
            writer.writerow([AffectationProfesseurClasseController._csv_escape(str(row.get(key) or "")) for _, key in _CSV_COLS])
        content = output.getvalue().encode("utf-8")
        return Response(
            200,
            content,
            "text/csv; charset=utf-8",
            headers={
                "Content-Disposition": 'attachment; filename="affectation_professeur_classes.csv"',
                "Cache-Control": "no-store",
            },
        )
