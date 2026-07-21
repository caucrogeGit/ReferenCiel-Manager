import csv
import io
from core.http.request import Request
from core.http.response import Response
from core.mvc.controller import BaseController
from core.mvc.view.pagination import Pagination
from mvc.models.formation_niveau_model import (
    get_formation_niveau_by_id, add_formation_niveau, update_formation_niveau, delete_formation_niveau, bulk_delete_formation_niveaus,
    count_formation_niveaus, find_formation_niveaus_paginated, find_formation_niveaus_for_export,
    get_formation_choices, get_niveau_classe_choices,
)
from mvc.forms.formation_niveau_form import FormationNiveauForm
from core.security.session import get_flash, get_session_id


def _form_data_from_formation_niveau(record: dict) -> dict:
    """Convertit les colonnes SQL vers les noms de champs du formulaire."""
    return {
        "code": record.get("Code"),
        "libelle": record.get("Libelle"),
        "ordre_indicatif": record.get("OrdreIndicatif"),
        "formation_id": record.get("formation_id"),
        "niveau_classe_id": record.get("niveau_classe_id"),
    }


def _formation_niveau_form_options():
    return {
        "formation_id_choices": get_formation_choices(),
        "niveau_classe_id_choices": get_niveau_classe_choices(),
    }


def _query_param(request, name, default=""):
    """Retourne le premier paramètre GET, au format parse_qs de Forge."""
    values = request.params.get(name, [default])
    return values[0] if values else default


def _is_hx_request(request):
    """Détecte une requête HTMX locale au CRUD généré."""
    return request.headers.get("HX-Request", "").lower() == "true"


_CSV_COLS = [('Code', 'Code'), ('Libelle', 'Libelle'), ('Ordre indicatif', 'OrdreIndicatif'), ('Formation id', 'formation_id_label'), ('Niveau classe id', 'niveau_classe_id_label')]


class FormationNiveauController(BaseController):

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
        if sort not in {"code", "libelle", "ordre_indicatif", "formation_id", "niveau_classe_id", "id"}:
            sort = ""
        direction = _query_param(request, "direction", "desc")
        if direction not in ("asc", "desc"):
            direction = "asc"
        limit  = 20
        formation_id_raw = _query_param(request, "formation_id").strip()
        formation_id_f = ""
        if formation_id_raw:
            try:
                formation_id_f = int(formation_id_raw)
            except (TypeError, ValueError):
                formation_id_f = ""
        niveau_classe_id_raw = _query_param(request, "niveau_classe_id").strip()
        niveau_classe_id_f = ""
        if niveau_classe_id_raw:
            try:
                niveau_classe_id_f = int(niveau_classe_id_raw)
            except (TypeError, ValueError):
                niveau_classe_id_f = ""
        relation_filters = {}
        relation_filters["formation_id"] = {"options": [{"id": value, "label": label} for value, label in get_formation_choices()]}
        relation_filters["niveau_classe_id"] = {"options": [{"id": value, "label": label} for value, label in get_niveau_classe_choices()]}
        _filters = {}
        if formation_id_f != "":
            _filters["formation_id"] = formation_id_f
        if niveau_classe_id_f != "":
            _filters["niveau_classe_id"] = niveau_classe_id_f
        total    = count_formation_niveaus(q or None, filters=_filters or None)
        pagination_state = Pagination(request, total, limit)
        limit = pagination_state.limit
        offset = pagination_state.offset
        empty_context = "search_filters" if q and _filters else ("search" if q else ("filters" if _filters else None))
        formation_niveaus = find_formation_niveaus_paginated(
            q=q or None, sort=sort or None, direction=direction,
            limit=limit, offset=offset, filters=_filters or None,
        )
        pagination = pagination_state.to_dict()
        pagination.update({
            "q": q, "sort": sort, "direction": direction,
            "filters": {"formation_id": formation_id_f, "niveau_classe_id": niveau_classe_id_f},
        })
        return {
                "formation_niveaus": formation_niveaus,
                "pagination": pagination,
                "empty_context": empty_context,
                "relation_filters": relation_filters,
                "flash": get_flash(get_session_id(request)),
            }

    @staticmethod
    def index(request: Request) -> Response:
        context = FormationNiveauController._list_context(request)
        template = "app/formation_niveau/_results.html" if _is_hx_request(request) else "app/formation_niveau/index.html"
        return BaseController.render(template, context=context, request=request)

    @staticmethod
    def new(request: Request) -> Response:
        form = FormationNiveauForm(**_formation_niveau_form_options())
        return BaseController.render("app/formation_niveau/form.html",
            context={
                "form": form,
                "action": "/formation_niveau/create",
                "titre": "Nouveau formation_niveau",
            },
            request=request)

    @staticmethod
    def create(request: Request) -> Response:
        form = FormationNiveauForm.from_request(request, **_formation_niveau_form_options())
        if not form.is_valid():
            return BaseController.validation_error("app/formation_niveau/form.html",
                context={
                    "form": form,
                    "action": "/formation_niveau/create",
                    "titre": "Nouveau formation_niveau",
                },
                request=request)
        add_formation_niveau(form.cleaned_data)
        return BaseController.redirect_with_flash(request, "/formation_niveau", "FormationNiveau créé.")

    @staticmethod
    def show(request: Request) -> Response:
        id = FormationNiveauController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        formation_niveau = get_formation_niveau_by_id(id)
        if formation_niveau is None:
            return BaseController.not_found()
        return BaseController.render("app/formation_niveau/show.html",
            context={"formation_niveau": formation_niveau, "flash": get_flash(get_session_id(request))},
            request=request)

    @staticmethod
    def edit(request: Request) -> Response:
        id = FormationNiveauController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        formation_niveau = get_formation_niveau_by_id(id)
        if formation_niveau is None:
            return BaseController.not_found()
        return BaseController.render("app/formation_niveau/form.html",
            context={
                "form": FormationNiveauForm(_form_data_from_formation_niveau(formation_niveau), **_formation_niveau_form_options()),
                "action": f"/formation_niveau/update/{id}",
                "titre": "Modifier formation_niveau",
            },
            request=request)

    @staticmethod
    def update(request: Request) -> Response:
        id = FormationNiveauController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        form = FormationNiveauForm.from_request(request, **_formation_niveau_form_options())
        if not form.is_valid():
            return BaseController.validation_error("app/formation_niveau/form.html",
                context={
                    "form": form,
                    "action": f"/formation_niveau/update/{id}",
                    "titre": "Modifier formation_niveau",
                },
                request=request)
        update_formation_niveau(id, form.cleaned_data)
        return BaseController.redirect_with_flash(
            request, f"/formation_niveau/show/{id}", "FormationNiveau mis à jour.")

    @staticmethod
    def destroy(request: Request) -> Response:
        id = FormationNiveauController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        delete_formation_niveau(id)
        if _is_hx_request(request):
            context = FormationNiveauController._list_context(request)
            return BaseController.render("app/formation_niveau/_results.html", context=context, request=request)
        return BaseController.redirect_with_flash(request, "/formation_niveau", "FormationNiveau supprimé.")


    @staticmethod
    def bulk_delete(request: Request) -> Response:
        ids = FormationNiveauController._parse_bulk_ids(request)
        if not ids:
            return BaseController.redirect_with_flash(request, "/formation_niveau", "Aucun élément sélectionné.")
        return BaseController.render("app/formation_niveau/bulk_delete_confirm.html",
            context={"ids": ids, "count": len(ids), "flash": get_flash(get_session_id(request))},
            request=request)

    @staticmethod
    def bulk_delete_confirm(request: Request) -> Response:
        ids = FormationNiveauController._parse_bulk_ids(request)
        if not ids:
            return BaseController.redirect_with_flash(request, "/formation_niveau", "Aucun élément sélectionné.")
        bulk_delete_formation_niveaus(ids)
        count = len(ids)
        return BaseController.redirect_with_flash(
            request, "/formation_niveau",
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
        if sort not in {"code", "libelle", "ordre_indicatif", "formation_id", "niveau_classe_id", "id"}:
            sort = ""
        direction = _query_param(request, "direction", "desc")
        if direction not in ("asc", "desc"):
            direction = "asc"
        formation_id_raw = _query_param(request, "formation_id").strip()
        formation_id_f = ""
        if formation_id_raw:
            try:
                formation_id_f = int(formation_id_raw)
            except (TypeError, ValueError):
                formation_id_f = ""
        niveau_classe_id_raw = _query_param(request, "niveau_classe_id").strip()
        niveau_classe_id_f = ""
        if niveau_classe_id_raw:
            try:
                niveau_classe_id_f = int(niveau_classe_id_raw)
            except (TypeError, ValueError):
                niveau_classe_id_f = ""
        _filters = {}
        if formation_id_f != "":
            _filters["formation_id"] = formation_id_f
        if niveau_classe_id_f != "":
            _filters["niveau_classe_id"] = niveau_classe_id_f
        rows = find_formation_niveaus_for_export(q=q or None, sort=sort or None, direction=direction, filters=_filters or None)
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_ALL)
        writer.writerow([header for header, _ in _CSV_COLS])
        for row in rows:
            writer.writerow([FormationNiveauController._csv_escape(str(row.get(key) or "")) for _, key in _CSV_COLS])
        content = output.getvalue().encode("utf-8")
        return Response(
            200,
            content,
            "text/csv; charset=utf-8",
            headers={
                "Content-Disposition": 'attachment; filename="formation_niveaus.csv"',
                "Cache-Control": "no-store",
            },
        )
