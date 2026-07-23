import csv
import io
from core.http.request import Request
from core.http.response import Response
from core.mvc.controller import BaseController
from core.mvc.view.pagination import Pagination
from mvc.models.progression_sequence_model import (
    get_progression_sequence_by_id, add_progression_sequence, update_progression_sequence, delete_progression_sequence, bulk_delete_progression_sequences,
    count_progression_sequences, find_progression_sequences_paginated, find_progression_sequences_for_export,
    get_eleve_choices, get_sequence_choices,
)
from mvc.forms.progression_sequence_form import ProgressionSequenceForm
from mvc.models.sequence_model import recalculer_statut as recalculer_statut_sequence
from core.security.session import get_flash, get_session_id


def _form_data_from_progression_sequence(record: dict) -> dict:
    """Convertit les colonnes SQL vers les noms de champs du formulaire."""
    return {
        "statut": record.get("Statut"),
        "date_debut": record.get("DateDebut"),
        "eleve_id": record.get("eleve_id"),
        "sequence_id": record.get("sequence_id"),
    }


def _progression_sequence_form_options():
    return {
        "eleve_id_choices": get_eleve_choices(),
        "sequence_id_choices": get_sequence_choices(),
    }


def _query_param(request, name, default=""):
    """Retourne le premier paramètre GET, au format parse_qs de Forge."""
    values = request.params.get(name, [default])
    return values[0] if values else default


def _is_hx_request(request):
    """Détecte une requête HTMX locale au CRUD généré."""
    return request.headers.get("HX-Request", "").lower() == "true"


_CSV_COLS = [('Statut', 'Statut'), ('Date debut', 'DateDebut'), ('Eleve id', 'eleve_id_label'), ('Séquence', 'sequence_id_label')]


class ProgressionSequenceController(BaseController):

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
        if sort not in {"statut", "date_debut", "eleve_id", "sequence_id", "id"}:
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
        sequence_id_raw = _query_param(request, "sequence_id").strip()
        sequence_id_f = ""
        if sequence_id_raw:
            try:
                sequence_id_f = int(sequence_id_raw)
            except (TypeError, ValueError):
                sequence_id_f = ""
        relation_filters = {}
        relation_filters["eleve_id"] = {"options": [{"id": value, "label": label} for value, label in get_eleve_choices()]}
        relation_filters["sequence_id"] = {"options": [{"id": value, "label": label} for value, label in get_sequence_choices()]}
        _filters = {}
        if eleve_id_f != "":
            _filters["eleve_id"] = eleve_id_f
        if sequence_id_f != "":
            _filters["sequence_id"] = sequence_id_f
        total    = count_progression_sequences(q or None, filters=_filters or None)
        pagination_state = Pagination(request, total, limit)
        limit = pagination_state.limit
        offset = pagination_state.offset
        empty_context = "search_filters" if q and _filters else ("search" if q else ("filters" if _filters else None))
        progression_sequences = find_progression_sequences_paginated(
            q=q or None, sort=sort or None, direction=direction,
            limit=limit, offset=offset, filters=_filters or None,
        )
        pagination = pagination_state.to_dict()
        pagination.update({
            "q": q, "sort": sort, "direction": direction,
            "filters": {"eleve_id": eleve_id_f, "sequence_id": sequence_id_f},
        })
        return {
                "progression_sequences": progression_sequences,
                "pagination": pagination,
                "empty_context": empty_context,
                "relation_filters": relation_filters,
                "flash": get_flash(get_session_id(request)),
            }

    @staticmethod
    def index(request: Request) -> Response:
        context = ProgressionSequenceController._list_context(request)
        template = "app/progression_sequence/_results.html" if _is_hx_request(request) else "app/progression_sequence/index.html"
        return BaseController.render(template, context=context, request=request)

    @staticmethod
    def new(request: Request) -> Response:
        form = ProgressionSequenceForm(**_progression_sequence_form_options())
        return BaseController.render("app/progression_sequence/form.html",
            context={
                "form": form,
                "action": "/progression_sequence/create",
                "titre": "Nouvelle progression de séquence",
            },
            request=request)

    @staticmethod
    def create(request: Request) -> Response:
        form = ProgressionSequenceForm.from_request(request, **_progression_sequence_form_options())
        if not form.is_valid():
            return BaseController.validation_error("app/progression_sequence/form.html",
                context={
                    "form": form,
                    "action": "/progression_sequence/create",
                    "titre": "Nouvelle progression de séquence",
                },
                request=request)
        add_progression_sequence(form.cleaned_data)
        # L'attribution à un élève fait passer la séquence en « attribue » (ADR-034).
        recalculer_statut_sequence(form.cleaned_data["sequence_id"])
        return BaseController.redirect_with_flash(request, "/progression_sequence", "Progression de séquence créée.")

    @staticmethod
    def show(request: Request) -> Response:
        id = ProgressionSequenceController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        progression_sequence = get_progression_sequence_by_id(id)
        if progression_sequence is None:
            return BaseController.not_found()
        return BaseController.render("app/progression_sequence/show.html",
            context={"progression_sequence": progression_sequence, "flash": get_flash(get_session_id(request))},
            request=request)

    @staticmethod
    def edit(request: Request) -> Response:
        id = ProgressionSequenceController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        progression_sequence = get_progression_sequence_by_id(id)
        if progression_sequence is None:
            return BaseController.not_found()
        return BaseController.render("app/progression_sequence/form.html",
            context={
                "form": ProgressionSequenceForm(_form_data_from_progression_sequence(progression_sequence), **_progression_sequence_form_options()),
                "action": f"/progression_sequence/update/{id}",
                "titre": "Modifier la progression de séquence",
            },
            request=request)

    @staticmethod
    def update(request: Request) -> Response:
        id = ProgressionSequenceController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        avant = get_progression_sequence_by_id(id)
        form = ProgressionSequenceForm.from_request(request, **_progression_sequence_form_options())
        if not form.is_valid():
            return BaseController.validation_error("app/progression_sequence/form.html",
                context={
                    "form": form,
                    "action": f"/progression_sequence/update/{id}",
                    "titre": "Modifier la progression de séquence",
                },
                request=request)
        update_progression_sequence(id, form.cleaned_data)
        # Un changement de séquence touche les DEUX séquences (ADR-034).
        if avant is not None:
            recalculer_statut_sequence(avant["sequence_id"])
        recalculer_statut_sequence(form.cleaned_data["sequence_id"])
        return BaseController.redirect_with_flash(
            request, f"/progression_sequence/show/{id}", "Progression de séquence mise à jour.")

    @staticmethod
    def destroy(request: Request) -> Response:
        id = ProgressionSequenceController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        progression = get_progression_sequence_by_id(id)
        delete_progression_sequence(id)
        # La dernière progression supprimée fait quitter « attribue » (ADR-034).
        if progression is not None:
            recalculer_statut_sequence(progression["sequence_id"])
        if _is_hx_request(request):
            context = ProgressionSequenceController._list_context(request)
            return BaseController.render("app/progression_sequence/_results.html", context=context, request=request)
        return BaseController.redirect_with_flash(request, "/progression_sequence", "Progression de séquence supprimée.")


    @staticmethod
    def bulk_delete(request: Request) -> Response:
        ids = ProgressionSequenceController._parse_bulk_ids(request)
        if not ids:
            return BaseController.redirect_with_flash(request, "/progression_sequence", "Aucun élément sélectionné.")
        return BaseController.render("app/progression_sequence/bulk_delete_confirm.html",
            context={"ids": ids, "count": len(ids), "flash": get_flash(get_session_id(request))},
            request=request)

    @staticmethod
    def bulk_delete_confirm(request: Request) -> Response:
        ids = ProgressionSequenceController._parse_bulk_ids(request)
        if not ids:
            return BaseController.redirect_with_flash(request, "/progression_sequence", "Aucun élément sélectionné.")
        sequences_touchees = {
            p["sequence_id"] for p in (get_progression_sequence_by_id(i) for i in ids) if p is not None
        }
        bulk_delete_progression_sequences(ids)
        for sequence_id in sequences_touchees:
            recalculer_statut_sequence(sequence_id)
        count = len(ids)
        return BaseController.redirect_with_flash(
            request, "/progression_sequence",
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
        if sort not in {"statut", "date_debut", "eleve_id", "sequence_id", "id"}:
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
        sequence_id_raw = _query_param(request, "sequence_id").strip()
        sequence_id_f = ""
        if sequence_id_raw:
            try:
                sequence_id_f = int(sequence_id_raw)
            except (TypeError, ValueError):
                sequence_id_f = ""
        _filters = {}
        if eleve_id_f != "":
            _filters["eleve_id"] = eleve_id_f
        if sequence_id_f != "":
            _filters["sequence_id"] = sequence_id_f
        rows = find_progression_sequences_for_export(q=q or None, sort=sort or None, direction=direction, filters=_filters or None)
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_ALL)
        writer.writerow([header for header, _ in _CSV_COLS])
        for row in rows:
            writer.writerow([ProgressionSequenceController._csv_escape(str(row.get(key) or "")) for _, key in _CSV_COLS])
        content = output.getvalue().encode("utf-8")
        return Response(
            200,
            content,
            "text/csv; charset=utf-8",
            headers={
                "Content-Disposition": 'attachment; filename="progression_sequences.csv"',
                "Cache-Control": "no-store",
            },
        )
