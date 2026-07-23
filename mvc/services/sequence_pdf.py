"""Construction du PDF d'une séquence (miroir de scenario_pdf).

Rassemble le contenu propre à la séquence — titre, cadre institutionnel
(SEQ-02), savoirs associés (connaissances structurées ADR-028 ou savoirs libres
ADR-030) et séances — puis rend le template `app/sequence_editeur/pdf.html` et
délègue la conversion HTML->PDF à `services.pdf.render_pdf`.
"""
from typing import Any

from core.templating.manager import template_manager

from mvc.models.sequence_model import get_sequence_by_id
from mvc.models.seance_model import get_seances_by_sequence
from mvc.models.element_seance_model import get_elements, TYPE_LABELS
from mvc.models.seance_connaissance_model import get_connaissances_retenues_agregees
from mvc.models.sequence_connaissance_model import (
    get_referentiel_id_for_sequence,
)
from mvc.models.savoir_libre_model import get_savoirs_libres
from mvc.services.pdf import render_pdf
from mvc.services.sequence_tunnel import duree_lisible


def assembler_sequence(sequence_id: int) -> dict[str, Any]:
    """Rassemble les données d'une séquence pour l'export (PDF, Markdown, JSON)."""
    sequence = get_sequence_by_id(sequence_id)
    if sequence is None:
        raise ValueError(f"séquence {sequence_id} introuvable")

    ref_id = get_referentiel_id_for_sequence(sequence_id)
    # Savoirs associés : connaissances structurées si référentiel (ADR-028),
    # sinon savoirs libres saisis par le professeur (ADR-030).
    connaissances: list[dict[str, Any]] = (
        get_connaissances_retenues_agregees(sequence_id, int(ref_id)) if ref_id else []
    )
    # Savoirs libres COMPLÉMENTAIRES (évolution ADR-030) : chargés même avec
    # un référentiel, ils s'ajoutent aux connaissances structurées.
    savoirs_libres: list[str] = [str(s["Libelle"]) for s in get_savoirs_libres(sequence_id)]
    seances = get_seances_by_sequence(sequence_id)
    for seance in seances:
        elements = get_elements(seance["Id"])
        for el in elements:
            el["type_label"] = TYPE_LABELS.get(str(el["Type"]), el["Type"])
        seance["elements"] = elements
    # Valeurs DÉRIVÉES (jamais saisies), écrasant les colonnes historiques dans
    # tous les exports : durée = cumul des séances, prérequis = agrégation des
    # prérequis de séance.
    total = sum(int(s["DureeEstimeeMinutes"]) for s in seances if s.get("DureeEstimeeMinutes"))
    sequence["DureeEstimee"] = duree_lisible(total or None)
    lignes_prerequis = [
        f"Séance {s['Ordre']} : {s['Prerequis']}" for s in seances if s.get("Prerequis")
    ]
    sequence["Prerequis"] = "\n".join(lignes_prerequis) or None
    return {
        "sequence": sequence,
        "connaissances": connaissances,
        "savoirs_libres": savoirs_libres,
        "seances": seances,
    }


def construire_pdf(sequence_id: int) -> bytes:
    """Assemble le PDF d'une séquence."""
    html = template_manager.render(
        "app/sequence_editeur/pdf.html", assembler_sequence(sequence_id)
    )
    return render_pdf(html)
