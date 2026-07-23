"""Attributions d'une séquence (ADR-035) : qui travaille sur quoi.

Remplace, pour l'usage courant, le CRUD « Progressions » du menu Exécution :
la page s'ouvre depuis la carte de la séquence (publiée ou attribuée) et
permet d'attribuer par classe entière ou par élève, puis de retirer une
attribution tant que l'élève n'a pas commencé (RESTRICT au contrat).
"""

from core.http.request import Request
from core.http.response import Response
from core.mvc.controller import BaseController
from core.security.session import get_flash, get_session_id

from mvc.helpers.groupes import grouper
from mvc.models.sequence_model import get_sequence_by_id, recalculer_statut
from mvc.models.sequence_attribution_model import (
    attributions,
    attribuer_classe,
    attribuer_eleve,
    classes_avec_effectif,
    eleves_non_attribues,
    motif_blocage_retrait,
    retirer,
)
from mvc.services.sequence_tunnel import parse_id


def _libelle_classe(row):
    if not row.get("classe_code"):
        return None
    libelle = row.get("classe_libelle")
    return f"{row['classe_code']} — {libelle}" if libelle else str(row["classe_code"])


class SequenceAttributionController(BaseController):

    @staticmethod
    def _sequence_attribuable(request: Request):
        """Séquence de la route, ou None si absente/non publiée."""
        sid = parse_id(request.route("id"))
        if sid is None:
            return None
        sequence = get_sequence_by_id(sid)
        if sequence is None or sequence.get("Statut") not in ("publie", "attribue"):
            return None
        return sequence

    @staticmethod
    def index(request: Request) -> Response:
        sequence = SequenceAttributionController._sequence_attribuable(request)
        if sequence is None:
            return BaseController.redirect_with_flash(
                request, "/sequence",
                "Attribution possible sur une séquence publiée (au moins une séance liée).",
                "error")
        lignes = attributions(int(sequence["Id"]))
        # Motif de blocage calculé par ligne : le bouton Retirer se neutralise
        # avec l'explication, plutôt que d'échouer après clic.
        for ligne in lignes:
            ligne["motif_blocage"] = motif_blocage_retrait(int(ligne["Id"]))
        context = {
            "sequence": sequence,
            "groupes": grouper(lignes, _libelle_classe, "Sans classe"),
            "classes": classes_avec_effectif(),
            "eleves_libres": eleves_non_attribues(int(sequence["Id"])),
            "flash": get_flash(get_session_id(request)),
        }
        return BaseController.render(
            "app/sequence_attribution/index.html", context=context, request=request)

    @staticmethod
    def attribuer_a_classe(request: Request) -> Response:
        sequence = SequenceAttributionController._sequence_attribuable(request)
        if sequence is None:
            return BaseController.not_found()
        sid = int(sequence["Id"])
        classe_id = parse_id(request.form("classe_id", ""))
        if classe_id is None:
            return BaseController.redirect_with_flash(
                request, f"/sequence/{sid}/attributions", "Choisissez une classe.", "error")
        crees = attribuer_classe(sid, classe_id)
        recalculer_statut(sid)
        return BaseController.redirect_with_flash(
            request, f"/sequence/{sid}/attributions",
            f"{crees} élève(s) attribué(s) (les attributions existantes sont conservées).")

    @staticmethod
    def attribuer_a_eleve(request: Request) -> Response:
        sequence = SequenceAttributionController._sequence_attribuable(request)
        if sequence is None:
            return BaseController.not_found()
        sid = int(sequence["Id"])
        eleve_id = parse_id(request.form("eleve_id", ""))
        if eleve_id is None:
            return BaseController.redirect_with_flash(
                request, f"/sequence/{sid}/attributions", "Choisissez un élève.", "error")
        crees = attribuer_eleve(sid, eleve_id)
        recalculer_statut(sid)
        message = "Élève attribué." if crees else "Cet élève était déjà attribué."
        return BaseController.redirect_with_flash(
            request, f"/sequence/{sid}/attributions", message)

    @staticmethod
    def retirer_attribution(request: Request) -> Response:
        sequence = SequenceAttributionController._sequence_attribuable(request)
        if sequence is None:
            return BaseController.not_found()
        sid = int(sequence["Id"])
        pid = parse_id(request.route("pid"))
        if pid is None:
            return BaseController.not_found()
        motif = motif_blocage_retrait(pid)
        if motif is not None:
            return BaseController.redirect_with_flash(
                request, f"/sequence/{sid}/attributions",
                f"Retrait impossible : cette attribution porte {motif}.", "error")
        retirer(pid)
        recalculer_statut(sid)
        return BaseController.redirect_with_flash(
            request, f"/sequence/{sid}/attributions", "Attribution retirée.")
