import csv
import io
from core.http.request import Request
from core.http.response import Response
from core.mvc.controller import BaseController
from core.mvc.view.pagination import Pagination
from mvc.models.sequence_model import (
    get_sequences, get_sequence_by_id, add_sequence, update_sequence, delete_sequence, bulk_delete_sequences,
    count_sequences, find_sequences_paginated, find_sequences_for_export,
    get_niveau_classe_choices,
)
from mvc.forms.sequence_form import SequenceForm
from mvc.controllers.sequence_connaissance_controller import contexte_connaissances
from mvc.models.referentiel_atelier_model import list_referentiels
from mvc.services.sequence_pdf import construire_pdf
from mvc.services.sequence_export import construire_json, construire_markdown
from mvc.services.scenario_tunnel import slug
from core.security.session import get_flash, get_session_id


def _form_data_from_sequence(record: dict) -> dict:
    """Convertit les colonnes SQL vers les noms de champs du formulaire."""
    return {
        "identifiant": record.get("Identifiant"),
        "titre": record.get("Titre"),
        "presentation": record.get("Presentation"),
        "statut": record.get("Statut"),
        "activite_glissante": record.get("ActiviteGlissante"),
        "ordre_impose": record.get("OrdreImpose"),
        "prerequis": record.get("Prerequis"),
        "positionnement_progression": record.get("PositionnementProgression"),
        "duree_estimee": record.get("DureeEstimee"),
        "modalites_evaluation": record.get("ModalitesEvaluation"),
        "niveau_classe_id": record.get("niveau_classe_id"),
    }


def _sequence_form_options():
    return {
        "niveau_classe_id_choices": get_niveau_classe_choices(),
    }


def _query_param(request, name, default=""):
    """Retourne le premier paramètre GET, au format parse_qs de Forge."""
    values = request.params.get(name, [default])
    return values[0] if values else default


def _is_hx_request(request):
    """Détecte une requête HTMX locale au CRUD généré."""
    return request.headers.get("HX-Request", "").lower() == "true"


_CSV_COLS = [('Identifiant', 'Identifiant'), ('Titre', 'Titre'), ('Presentation', 'Presentation'), ('Statut', 'Statut'), ('Activite glissante', 'ActiviteGlissante'), ('Ordre impose', 'OrdreImpose'), ('Niveau classe id', 'niveau_classe_id_label')]


class SequenceController(BaseController):

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
        if sort not in {"identifiant", "titre", "presentation", "statut", "activite_glissante", "ordre_impose", "niveau_classe_id", "id"}:
            sort = ""
        direction = _query_param(request, "direction", "desc")
        if direction not in ("asc", "desc"):
            direction = "asc"
        limit  = 20
        niveau_classe_id_raw = _query_param(request, "niveau_classe_id").strip()
        niveau_classe_id_f = ""
        if niveau_classe_id_raw:
            try:
                niveau_classe_id_f = int(niveau_classe_id_raw)
            except (TypeError, ValueError):
                niveau_classe_id_f = ""
        relation_filters = {}
        relation_filters["niveau_classe_id"] = {"options": [{"id": value, "label": label} for value, label in get_niveau_classe_choices()]}
        _filters = {}
        if niveau_classe_id_f != "":
            _filters["niveau_classe_id"] = niveau_classe_id_f
        total    = count_sequences(q or None, filters=_filters or None)
        pagination_state = Pagination(request, total, limit)
        limit = pagination_state.limit
        offset = pagination_state.offset
        empty_context = "search_filters" if q and _filters else ("search" if q else ("filters" if _filters else None))
        sequences = find_sequences_paginated(
            q=q or None, sort=sort or None, direction=direction,
            limit=limit, offset=offset, filters=_filters or None,
        )
        pagination = pagination_state.to_dict()
        pagination.update({
            "q": q, "sort": sort, "direction": direction,
            "filters": {"niveau_classe_id": niveau_classe_id_f},
        })
        return {
                "sequences": sequences,
                "pagination": pagination,
                "empty_context": empty_context,
                "relation_filters": relation_filters,
                "flash": get_flash(get_session_id(request)),
            }

    @staticmethod
    def index(request: Request) -> Response:
        # Grille de cartes (même design que la liste des scénarios) : toutes les
        # séquences, création inline en tête. Le tri/filtre/CSV restent servis par
        # leurs routes dédiées, mais ne surchargent plus cette page.
        context = {
            "sequences": get_sequences(),
            "referentiels": list_referentiels(),
            "flash": get_flash(get_session_id(request)),
        }
        return BaseController.render("app/sequence/index.html", context=context, request=request)

    @staticmethod
    def new(request: Request) -> Response:
        form = SequenceForm(**_sequence_form_options())
        return BaseController.render("app/sequence/form.html",
            context={
                "form": form,
                "action": "/sequence/create",
                "titre": "Nouvelle séquence",
            },
            request=request)

    @staticmethod
    def create(request: Request) -> Response:
        form = SequenceForm.from_request(request, **_sequence_form_options())
        if not form.is_valid():
            return BaseController.validation_error("app/sequence/form.html",
                context={
                    "form": form,
                    "action": "/sequence/create",
                    "titre": "Nouvelle séquence",
                },
                request=request)
        add_sequence(form.cleaned_data)
        return BaseController.redirect_with_flash(request, "/sequence", "Séquence créée.")

    @staticmethod
    def show(request: Request) -> Response:
        id = SequenceController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        sequence = get_sequence_by_id(id)
        if sequence is None:
            return BaseController.not_found()
        context = {"sequence": sequence, "flash": get_flash(get_session_id(request))}
        context.update(contexte_connaissances(id))
        return BaseController.render("app/sequence/show.html",
            context=context,
            request=request)

    @staticmethod
    def edit(request: Request) -> Response:
        id = SequenceController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        sequence = get_sequence_by_id(id)
        if sequence is None:
            return BaseController.not_found()
        return BaseController.render("app/sequence/form.html",
            context={
                "form": SequenceForm(_form_data_from_sequence(sequence), **_sequence_form_options()),
                "action": f"/sequence/update/{id}",
                "titre": "Modifier la séquence",
            },
            request=request)

    @staticmethod
    def update(request: Request) -> Response:
        id = SequenceController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        form = SequenceForm.from_request(request, **_sequence_form_options())
        if not form.is_valid():
            return BaseController.validation_error("app/sequence/form.html",
                context={
                    "form": form,
                    "action": f"/sequence/update/{id}",
                    "titre": "Modifier la séquence",
                },
                request=request)
        update_sequence(id, form.cleaned_data)
        return BaseController.redirect_with_flash(
            request, f"/sequence/show/{id}", "Séquence mise à jour.")

    @staticmethod
    def _telecharger(request, extension, mime, construire):
        """Télécharge un export de la séquence (PDF/MarkDown/JSON). Pas de verrou
        de finalisation côté séquence (contrairement au scénario)."""
        id = SequenceController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        sequence = get_sequence_by_id(id)
        if sequence is None:
            return BaseController.not_found()
        nom = slug(str(sequence.get("Titre") or "sequence"))
        return Response(
            200,
            construire(id),
            mime,
            headers={"Content-Disposition": f'attachment; filename="sequence-{nom}.{extension}"'},
        )

    @staticmethod
    def telecharger_pdf(request: Request) -> Response:
        return SequenceController._telecharger(request, "pdf", "application/pdf", construire_pdf)

    @staticmethod
    def telecharger_md(request: Request) -> Response:
        return SequenceController._telecharger(request, "md", "text/markdown; charset=utf-8", construire_markdown)

    @staticmethod
    def telecharger_json(request: Request) -> Response:
        return SequenceController._telecharger(request, "json", "application/json; charset=utf-8", construire_json)

    @staticmethod
    def destroy(request: Request) -> Response:
        id = SequenceController._parse_id(request.route("id"))
        if id is None:
            return BaseController.not_found()
        delete_sequence(id)
        if _is_hx_request(request):
            context = SequenceController._list_context(request)
            return BaseController.render("app/sequence/_results.html", context=context, request=request)
        return BaseController.redirect_with_flash(request, "/sequence", "Séquence supprimée.")


    @staticmethod
    def bulk_delete(request: Request) -> Response:
        ids = SequenceController._parse_bulk_ids(request)
        if not ids:
            return BaseController.redirect_with_flash(request, "/sequence", "Aucun élément sélectionné.")
        return BaseController.render("app/sequence/bulk_delete_confirm.html",
            context={"ids": ids, "count": len(ids), "flash": get_flash(get_session_id(request))},
            request=request)

    @staticmethod
    def bulk_delete_confirm(request: Request) -> Response:
        ids = SequenceController._parse_bulk_ids(request)
        if not ids:
            return BaseController.redirect_with_flash(request, "/sequence", "Aucun élément sélectionné.")
        bulk_delete_sequences(ids)
        count = len(ids)
        return BaseController.redirect_with_flash(
            request, "/sequence",
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
        if sort not in {"identifiant", "titre", "presentation", "statut", "activite_glissante", "ordre_impose", "niveau_classe_id", "id"}:
            sort = ""
        direction = _query_param(request, "direction", "desc")
        if direction not in ("asc", "desc"):
            direction = "asc"
        niveau_classe_id_raw = _query_param(request, "niveau_classe_id").strip()
        niveau_classe_id_f = ""
        if niveau_classe_id_raw:
            try:
                niveau_classe_id_f = int(niveau_classe_id_raw)
            except (TypeError, ValueError):
                niveau_classe_id_f = ""
        _filters = {}
        if niveau_classe_id_f != "":
            _filters["niveau_classe_id"] = niveau_classe_id_f
        rows = find_sequences_for_export(q=q or None, sort=sort or None, direction=direction, filters=_filters or None)
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_ALL)
        writer.writerow([header for header, _ in _CSV_COLS])
        for row in rows:
            writer.writerow([SequenceController._csv_escape(str(row.get(key) or "")) for _, key in _CSV_COLS])
        content = output.getvalue().encode("utf-8")
        return Response(
            200,
            content,
            "text/csv; charset=utf-8",
            headers={
                "Content-Disposition": 'attachment; filename="sequences.csv"',
                "Cache-Control": "no-store",
            },
        )
