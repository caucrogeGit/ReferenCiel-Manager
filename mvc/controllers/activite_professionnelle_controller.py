import csv
import io
from core.http.request import Request
from core.http.response import Response
from core.mvc.controller import BaseController
from core.mvc.view.pagination import Pagination
from mvc.models.activite_professionnelle_model import (
    get_activite_professionnelle_by_id, add_activite_professionnelle, update_activite_professionnelle, delete_activite_professionnelle, bulk_delete_activite_professionnelles,
    count_activite_professionnelles, find_activite_professionnelles_paginated, find_activite_professionnelles_for_export,
    get_referentiel_niveau_classe_choices, get_pole_activite_choices, get_competence_choices,
    get_activite_professionnelle_competence_ids, add_activite_professionnelle_competence_ids, sync_activite_professionnelle_competence_ids, get_activite_professionnelle_competence_labels_by_activite_professionnelle_id, get_activite_professionnelle_competence_labels,
)
from mvc.forms.activite_professionnelle_form import ActiviteProfessionnelleForm
from core.security.session import get_flash, get_session_id


def _form_data_from_activite_professionnelle(record: dict) -> dict:
    """Convertit les colonnes SQL vers les noms de champs du formulaire."""
    return {
        "code": record.get("Code"),
        "intitule": record.get("Intitule"),
        "conditions_exercice": record.get("ConditionsExercice"),
        "referentiel_id": record.get("referentiel_id"),
        "pole_id": record.get("pole_id"),
        "created_at": record.get("CreatedAt"),
        "updated_at": record.get("UpdatedAt"),
    }


def _activite_professionnelle_form_options():
    return {
        "referentiel_id_choices": get_referentiel_niveau_classe_choices(),
        "pole_id_choices": get_pole_activite_choices(),
    }


def _query_param(request, name, default=""):
    """Retourne le premier paramètre GET, au format parse_qs de Forge."""
    values = request.params.get(name, [default])
    return values[0] if values else default


def _is_hx_request(request):
    """Détecte une requête HTMX locale au CRUD généré."""
    return request.headers.get("HX-Request", "").lower() == "true"


_CSV_COLS = [('Code', 'Code'), ('Intitule', 'Intitule'), ('Conditions exercice', 'ConditionsExercice'), ('Referentiel id', 'referentiel_id_label'), ('Pole id', 'pole_id_label'), ('Created at', 'CreatedAt'), ('Updated at', 'UpdatedAt')]


class ActiviteProfessionnelleController(BaseController):

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
        if sort not in {"code", "intitule", "conditions_exercice", "referentiel_id", "pole_id", "created_at", "updated_at", "id"}:
            sort = ""
        direction = _query_param(request, "direction", "desc")
        if direction not in ("asc", "desc"):
            direction = "asc"
        limit  = 20
        referentiel_id_raw = _query_param(request, "referentiel_id").strip()
        referentiel_id_f = ""
        if referentiel_id_raw:
            try:
                referentiel_id_f = int(referentiel_id_raw)
            except (TypeError, ValueError):
                referentiel_id_f = ""
        pole_id_raw = _query_param(request, "pole_id").strip()
        pole_id_f = ""
        if pole_id_raw:
            try:
                pole_id_f = int(pole_id_raw)
            except (TypeError, ValueError):
                pole_id_f = ""
        relation_filters = {}
        relation_filters["referentiel_id"] = {"options": [{"id": value, "label": label} for value, label in get_referentiel_niveau_classe_choices()]}
        relation_filters["pole_id"] = {"options": [{"id": value, "label": label} for value, label in get_pole_activite_choices()]}
        _filters = {}
        if referentiel_id_f != "":
            _filters["referentiel_id"] = referentiel_id_f
        if pole_id_f != "":
            _filters["pole_id"] = pole_id_f
        total    = count_activite_professionnelles(q or None, filters=_filters or None)
        pagination_state = Pagination(request, total, limit)
        limit = pagination_state.limit
        offset = pagination_state.offset
        empty_context = "search_filters" if q and _filters else ("search" if q else ("filters" if _filters else None))
        activite_professionnelles = find_activite_professionnelles_paginated(
            q=q or None, sort=sort or None, direction=direction,
            limit=limit, offset=offset, filters=_filters or None,
        )
        pagination = pagination_state.to_dict()
        pagination.update({
            "q": q, "sort": sort, "direction": direction,
            "filters": {"referentiel_id": referentiel_id_f, "pole_id": pole_id_f},
        })
        return {
                "activite_professionnelles": activite_professionnelles,
                "pagination": pagination,
                "empty_context": empty_context,
                "relation_filters": relation_filters,
                "flash": get_flash(get_session_id(request)),
                "competences_by_activite_professionnelle_id": get_activite_professionnelle_competence_labels_by_activite_professionnelle_id([row["Id"] for row in activite_professionnelles]),
            }

    @staticmethod
    def index(request: Request) -> Response:
        context = ActiviteProfessionnelleController._list_context(request)
        template = "app/activite_professionnelle/_results.html" if _is_hx_request(request) else "app/activite_professionnelle/index.html"
        return BaseController.render(template, context=context, request=request)

    @staticmethod
    def new(request: Request) -> Response:
        form = ActiviteProfessionnelleForm(**_activite_professionnelle_form_options())
        return BaseController.render("app/activite_professionnelle/form.html",
            context={
                "form": form,
                "action": "/activite_professionnelle/create",
                "titre": "Nouveau activite_professionnelle",
                "competence_choices": get_competence_choices(),
                "competence_ids_selected": [],
            },
            request=request)

    @staticmethod
    def create(request: Request) -> Response:
        form = ActiviteProfessionnelleForm.from_request(request, **_activite_professionnelle_form_options())
        competence_ids = ActiviteProfessionnelleController._parse_many_ids(request, "competence_ids")
        if not form.is_valid():
            return BaseController.validation_error("app/activite_professionnelle/form.html",
                context={
                    "form": form,
                    "action": "/activite_professionnelle/create",
                    "titre": "Nouveau activite_professionnelle",
                    "competence_choices": get_competence_choices(),
                    "competence_ids_selected": competence_ids,
                },
                request=request)
        created_id = add_activite_professionnelle(form.cleaned_data)
        add_activite_professionnelle_competence_ids(created_id, competence_ids)
        return BaseController.redirect_with_flash(request, "/activite_professionnelle", "ActiviteProfessionnelle créé.")

    @staticmethod
    def show(request: Request) -> Response:
        id = ActiviteProfessionnelleController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        activite_professionnelle = get_activite_professionnelle_by_id(id)
        if activite_professionnelle is None:
            return BaseController.not_found()
        competence_labels = get_activite_professionnelle_competence_labels(id)
        return BaseController.render("app/activite_professionnelle/show.html",
            context={"activite_professionnelle": activite_professionnelle, "flash": get_flash(get_session_id(request)), "competence_labels": competence_labels},
            request=request)

    @staticmethod
    def edit(request: Request) -> Response:
        id = ActiviteProfessionnelleController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        activite_professionnelle = get_activite_professionnelle_by_id(id)
        if activite_professionnelle is None:
            return BaseController.not_found()
        return BaseController.render("app/activite_professionnelle/form.html",
            context={
                "form": ActiviteProfessionnelleForm(_form_data_from_activite_professionnelle(activite_professionnelle), **_activite_professionnelle_form_options()),
                "action": f"/activite_professionnelle/update/{id}",
                "titre": "Modifier activite_professionnelle",
                "competence_choices": get_competence_choices(),
                "competence_ids_selected": get_activite_professionnelle_competence_ids(id),
            },
            request=request)

    @staticmethod
    def update(request: Request) -> Response:
        id = ActiviteProfessionnelleController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        form = ActiviteProfessionnelleForm.from_request(request, **_activite_professionnelle_form_options())
        competence_ids = ActiviteProfessionnelleController._parse_many_ids(request, "competence_ids")
        if not form.is_valid():
            return BaseController.validation_error("app/activite_professionnelle/form.html",
                context={
                    "form": form,
                    "action": f"/activite_professionnelle/update/{id}",
                    "titre": "Modifier activite_professionnelle",
                    "competence_choices": get_competence_choices(),
                    "competence_ids_selected": competence_ids,
                },
                request=request)
        update_activite_professionnelle(id, form.cleaned_data)
        sync_activite_professionnelle_competence_ids(id, competence_ids)
        return BaseController.redirect_with_flash(
            request, f"/activite_professionnelle/show/{id}", "ActiviteProfessionnelle mis à jour.")

    @staticmethod
    def destroy(request: Request) -> Response:
        id = ActiviteProfessionnelleController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        delete_activite_professionnelle(id)
        if _is_hx_request(request):
            context = ActiviteProfessionnelleController._list_context(request)
            return BaseController.render("app/activite_professionnelle/_results.html", context=context, request=request)
        return BaseController.redirect_with_flash(request, "/activite_professionnelle", "ActiviteProfessionnelle supprimé.")


    @staticmethod
    def bulk_delete(request: Request) -> Response:
        ids = ActiviteProfessionnelleController._parse_bulk_ids(request)
        if not ids:
            return BaseController.redirect_with_flash(request, "/activite_professionnelle", "Aucun élément sélectionné.")
        return BaseController.render("app/activite_professionnelle/bulk_delete_confirm.html",
            context={"ids": ids, "count": len(ids), "flash": get_flash(get_session_id(request))},
            request=request)

    @staticmethod
    def bulk_delete_confirm(request: Request) -> Response:
        ids = ActiviteProfessionnelleController._parse_bulk_ids(request)
        if not ids:
            return BaseController.redirect_with_flash(request, "/activite_professionnelle", "Aucun élément sélectionné.")
        bulk_delete_activite_professionnelles(ids)
        count = len(ids)
        return BaseController.redirect_with_flash(
            request, "/activite_professionnelle",
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
        if sort not in {"code", "intitule", "conditions_exercice", "referentiel_id", "pole_id", "created_at", "updated_at", "id"}:
            sort = ""
        direction = _query_param(request, "direction", "desc")
        if direction not in ("asc", "desc"):
            direction = "asc"
        referentiel_id_raw = _query_param(request, "referentiel_id").strip()
        referentiel_id_f = ""
        if referentiel_id_raw:
            try:
                referentiel_id_f = int(referentiel_id_raw)
            except (TypeError, ValueError):
                referentiel_id_f = ""
        pole_id_raw = _query_param(request, "pole_id").strip()
        pole_id_f = ""
        if pole_id_raw:
            try:
                pole_id_f = int(pole_id_raw)
            except (TypeError, ValueError):
                pole_id_f = ""
        _filters = {}
        if referentiel_id_f != "":
            _filters["referentiel_id"] = referentiel_id_f
        if pole_id_f != "":
            _filters["pole_id"] = pole_id_f
        rows = find_activite_professionnelles_for_export(q=q or None, sort=sort or None, direction=direction, filters=_filters or None)
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_ALL)
        writer.writerow([header for header, _ in _CSV_COLS])
        for row in rows:
            writer.writerow([ActiviteProfessionnelleController._csv_escape(str(row.get(key) or "")) for _, key in _CSV_COLS])
        content = output.getvalue().encode("utf-8")
        return Response(
            200,
            content,
            "text/csv; charset=utf-8",
            headers={
                "Content-Disposition": 'attachment; filename="activite_professionnelles.csv"',
                "Cache-Control": "no-store",
            },
        )
