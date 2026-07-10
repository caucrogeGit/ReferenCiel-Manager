import csv
import io
from core.http.request import Request
from core.http.response import Response
from core.mvc.controller import BaseController
from core.mvc.view.pagination import Pagination
from mvc.models.annee_scolaire_model import (
    get_annee_scolaire_by_id, add_annee_scolaire, update_annee_scolaire, delete_annee_scolaire, bulk_delete_annee_scolaires,
    count_annee_scolaires, find_annee_scolaires_paginated, find_annee_scolaires_for_export,
)
from mvc.forms.annee_scolaire_form import AnneeScolaireForm
from mvc.helpers.flash import render_flash_html


def _form_data_from_annee_scolaire(record: dict) -> dict:
    """Convertit les colonnes SQL vers les noms de champs du formulaire."""
    return {
        "libelle": record.get("Libelle"),
        "date_debut": record.get("DateDebut"),
        "date_fin": record.get("DateFin"),
        "active": record.get("Active"),
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


_CSV_COLS = [('Libelle', 'Libelle'), ('Date debut', 'DateDebut'), ('Date fin', 'DateFin'), ('Active', 'Active'), ('Created at', 'CreatedAt'), ('Updated at', 'UpdatedAt')]


class AnneeScolaireController(BaseController):

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
        if sort not in {"libelle", "date_debut", "date_fin", "active", "created_at", "updated_at", "id"}:
            sort = ""
        direction = _query_param(request, "direction", "desc")
        if direction not in ("asc", "desc"):
            direction = "asc"
        limit  = 20
        relation_filters = {}
        total    = count_annee_scolaires(q or None)
        pagination_state = Pagination(request, total, limit)
        limit = pagination_state.limit
        offset = pagination_state.offset
        empty_context = "search" if q else None
        annee_scolaires = find_annee_scolaires_paginated(
            q=q or None, sort=sort or None, direction=direction,
            limit=limit, offset=offset,
        )
        pagination = pagination_state.to_dict()
        pagination.update({
            "q": q, "sort": sort, "direction": direction,
            "filters": {},
        })
        return {
                "annee_scolaires": annee_scolaires,
                "pagination": pagination,
                "empty_context": empty_context,
                "relation_filters": relation_filters,
                "flash_html": render_flash_html(request),
            }

    @staticmethod
    def index(request: Request) -> Response:
        context = AnneeScolaireController._list_context(request)
        template = "app/annee_scolaire/_results.html" if _is_hx_request(request) else "app/annee_scolaire/index.html"
        return BaseController.render(template, context=context, request=request)

    @staticmethod
    def new(request: Request) -> Response:
        form = AnneeScolaireForm()
        return BaseController.render("app/annee_scolaire/form.html",
            context={
                "form": form,
                "action": "/annee_scolaire/create",
                "titre": "Nouveau annee_scolaire",
            },
            request=request)

    @staticmethod
    def create(request: Request) -> Response:
        form = AnneeScolaireForm.from_request(request)
        if not form.is_valid():
            return BaseController.validation_error("app/annee_scolaire/form.html",
                context={
                    "form": form,
                    "action": "/annee_scolaire/create",
                    "titre": "Nouveau annee_scolaire",
                },
                request=request)
        add_annee_scolaire(form.cleaned_data)
        return BaseController.redirect_with_flash(request, "/annee_scolaire", "AnneeScolaire créé.")

    @staticmethod
    def show(request: Request) -> Response:
        id = AnneeScolaireController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        annee_scolaire = get_annee_scolaire_by_id(id)
        if annee_scolaire is None:
            return BaseController.not_found()
        return BaseController.render("app/annee_scolaire/show.html",
            context={"annee_scolaire": annee_scolaire, "flash_html": render_flash_html(request)},
            request=request)

    @staticmethod
    def edit(request: Request) -> Response:
        id = AnneeScolaireController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        annee_scolaire = get_annee_scolaire_by_id(id)
        if annee_scolaire is None:
            return BaseController.not_found()
        return BaseController.render("app/annee_scolaire/form.html",
            context={
                "form": AnneeScolaireForm(_form_data_from_annee_scolaire(annee_scolaire)),
                "action": f"/annee_scolaire/update/{id}",
                "titre": "Modifier annee_scolaire",
            },
            request=request)

    @staticmethod
    def update(request: Request) -> Response:
        id = AnneeScolaireController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        form = AnneeScolaireForm.from_request(request)
        if not form.is_valid():
            return BaseController.validation_error("app/annee_scolaire/form.html",
                context={
                    "form": form,
                    "action": f"/annee_scolaire/update/{id}",
                    "titre": "Modifier annee_scolaire",
                },
                request=request)
        update_annee_scolaire(id, form.cleaned_data)
        return BaseController.redirect_with_flash(
            request, f"/annee_scolaire/show/{id}", "AnneeScolaire mis à jour.")

    @staticmethod
    def destroy(request: Request) -> Response:
        id = AnneeScolaireController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        delete_annee_scolaire(id)
        if _is_hx_request(request):
            context = AnneeScolaireController._list_context(request)
            return BaseController.render("app/annee_scolaire/_results.html", context=context, request=request)
        return BaseController.redirect_with_flash(request, "/annee_scolaire", "AnneeScolaire supprimé.")


    @staticmethod
    def bulk_delete(request: Request) -> Response:
        ids = AnneeScolaireController._parse_bulk_ids(request)
        if not ids:
            return BaseController.redirect_with_flash(request, "/annee_scolaire", "Aucun élément sélectionné.")
        return BaseController.render("app/annee_scolaire/bulk_delete_confirm.html",
            context={"ids": ids, "count": len(ids), "flash_html": render_flash_html(request)},
            request=request)

    @staticmethod
    def bulk_delete_confirm(request: Request) -> Response:
        ids = AnneeScolaireController._parse_bulk_ids(request)
        if not ids:
            return BaseController.redirect_with_flash(request, "/annee_scolaire", "Aucun élément sélectionné.")
        bulk_delete_annee_scolaires(ids)
        count = len(ids)
        return BaseController.redirect_with_flash(
            request, "/annee_scolaire",
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
        if sort not in {"libelle", "date_debut", "date_fin", "active", "created_at", "updated_at", "id"}:
            sort = ""
        direction = _query_param(request, "direction", "desc")
        if direction not in ("asc", "desc"):
            direction = "asc"
        rows = find_annee_scolaires_for_export(q=q or None, sort=sort or None, direction=direction)
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_ALL)
        writer.writerow([header for header, _ in _CSV_COLS])
        for row in rows:
            writer.writerow([AnneeScolaireController._csv_escape(str(row.get(key) or "")) for _, key in _CSV_COLS])
        content = output.getvalue().encode("utf-8")
        return Response(
            200,
            content,
            "text/csv; charset=utf-8",
            headers={
                "Content-Disposition": 'attachment; filename="annee_scolaires.csv"',
                "Cache-Control": "no-store",
            },
        )
