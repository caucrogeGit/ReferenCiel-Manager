import csv
import io
from core.http.request import Request
from core.http.response import Response
from core.mvc.controller import BaseController
from core.mvc.view.pagination import Pagination
from mvc.models.professeur_model import (
    get_professeur_by_id, add_professeur, update_professeur, delete_professeur, bulk_delete_professeurs,
    count_professeurs, find_professeurs_paginated, find_professeurs_for_export,
)
from mvc.forms.professeur_form import ProfesseurForm
from core.security.session import get_flash, get_session_id


def _form_data_from_professeur(record: dict) -> dict:
    """Convertit les colonnes SQL vers les noms de champs du formulaire."""
    return {
        "nom": record.get("Nom"),
        "prenom": record.get("Prenom"),
        "user_id": record.get("UserId"),
        "created_at": record.get("CreatedAt"),
        "updated_at": record.get("UpdatedAt"),
    }


def _query_param(request, name, default=""):
    """Retourne le premier paramètre GET, au format parse_qs de Forge."""
    values = request.params.get(name, [default])
    return values[0] if values else default


def _is_hx_request(request):
    """Détecte une requête HTMX locale au CRUD généré."""
    return request.headers.get("HX-Request", "").lower() == "true"


_CSV_COLS = [('Nom', 'Nom'), ('Prenom', 'Prenom'), ('User id', 'UserId'), ('Created at', 'CreatedAt'), ('Updated at', 'UpdatedAt')]


class ProfesseurController(BaseController):

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
        if sort not in {"nom", "prenom", "user_id", "created_at", "updated_at", "id"}:
            sort = ""
        direction = _query_param(request, "direction", "desc")
        if direction not in ("asc", "desc"):
            direction = "asc"
        limit  = 20
        relation_filters = {}
        total    = count_professeurs(q or None)
        pagination_state = Pagination(request, total, limit)
        limit = pagination_state.limit
        offset = pagination_state.offset
        empty_context = "search" if q else None
        professeurs = find_professeurs_paginated(
            q=q or None, sort=sort or None, direction=direction,
            limit=limit, offset=offset,
        )
        pagination = pagination_state.to_dict()
        pagination.update({
            "q": q, "sort": sort, "direction": direction,
            "filters": {},
        })
        return {
                "professeurs": professeurs,
                "pagination": pagination,
                "empty_context": empty_context,
                "relation_filters": relation_filters,
                "flash": get_flash(get_session_id(request)),
            }

    @staticmethod
    def index(request: Request) -> Response:
        context = ProfesseurController._list_context(request)
        template = "professeur/_results.html" if _is_hx_request(request) else "professeur/index.html"
        return BaseController.render(template, context=context, request=request)

    @staticmethod
    def new(request: Request) -> Response:
        form = ProfesseurForm()
        return BaseController.render("professeur/form.html",
            context={
                "form": form,
                "action": "/professeur/create",
                "titre": "Nouveau professeur",
            },
            request=request)

    @staticmethod
    def create(request: Request) -> Response:
        form = ProfesseurForm.from_request(request)
        if not form.is_valid():
            return BaseController.validation_error("professeur/form.html",
                context={
                    "form": form,
                    "action": "/professeur/create",
                    "titre": "Nouveau professeur",
                },
                request=request)
        add_professeur(form.cleaned_data)
        return BaseController.redirect_with_flash(request, "/professeur", "Professeur créé.")

    @staticmethod
    def show(request: Request) -> Response:
        id = ProfesseurController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        professeur = get_professeur_by_id(id)
        if professeur is None:
            return BaseController.not_found()
        return BaseController.render("professeur/show.html",
            context={"professeur": professeur, "flash": get_flash(get_session_id(request))},
            request=request)

    @staticmethod
    def edit(request: Request) -> Response:
        id = ProfesseurController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        professeur = get_professeur_by_id(id)
        if professeur is None:
            return BaseController.not_found()
        return BaseController.render("professeur/form.html",
            context={
                "form": ProfesseurForm(_form_data_from_professeur(professeur)),
                "action": f"/professeur/update/{id}",
                "titre": "Modifier professeur",
            },
            request=request)

    @staticmethod
    def update(request: Request) -> Response:
        id = ProfesseurController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        form = ProfesseurForm.from_request(request)
        if not form.is_valid():
            return BaseController.validation_error("professeur/form.html",
                context={
                    "form": form,
                    "action": f"/professeur/update/{id}",
                    "titre": "Modifier professeur",
                },
                request=request)
        update_professeur(id, form.cleaned_data)
        return BaseController.redirect_with_flash(
            request, f"/professeur/show/{id}", "Professeur mis à jour.")

    @staticmethod
    def destroy(request: Request) -> Response:
        id = ProfesseurController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        delete_professeur(id)
        if _is_hx_request(request):
            context = ProfesseurController._list_context(request)
            return BaseController.render("professeur/_results.html", context=context, request=request)
        return BaseController.redirect_with_flash(request, "/professeur", "Professeur supprimé.")


    @staticmethod
    def bulk_delete(request: Request) -> Response:
        ids = ProfesseurController._parse_bulk_ids(request)
        if not ids:
            return BaseController.redirect_with_flash(request, "/professeur", "Aucun élément sélectionné.")
        return BaseController.render("professeur/bulk_delete_confirm.html",
            context={"ids": ids, "count": len(ids), "flash": get_flash(get_session_id(request))},
            request=request)

    @staticmethod
    def bulk_delete_confirm(request: Request) -> Response:
        ids = ProfesseurController._parse_bulk_ids(request)
        if not ids:
            return BaseController.redirect_with_flash(request, "/professeur", "Aucun élément sélectionné.")
        bulk_delete_professeurs(ids)
        count = len(ids)
        return BaseController.redirect_with_flash(
            request, "/professeur",
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
        if sort not in {"nom", "prenom", "user_id", "created_at", "updated_at", "id"}:
            sort = ""
        direction = _query_param(request, "direction", "desc")
        if direction not in ("asc", "desc"):
            direction = "asc"
        rows = find_professeurs_for_export(q=q or None, sort=sort or None, direction=direction)
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_ALL)
        writer.writerow([header for header, _ in _CSV_COLS])
        for row in rows:
            writer.writerow([ProfesseurController._csv_escape(str(row.get(key) or "")) for _, key in _CSV_COLS])
        content = output.getvalue().encode("utf-8")
        return Response(
            200,
            content,
            "text/csv; charset=utf-8",
            headers={
                "Content-Disposition": 'attachment; filename="professeurs.csv"',
                "Cache-Control": "no-store",
            },
        )
