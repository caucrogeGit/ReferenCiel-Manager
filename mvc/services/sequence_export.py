"""Export d'une séquence en **Markdown** et **JSON** (à côté du PDF).

Réutilise l'assemblage commun de `sequence_pdf.assembler_sequence`. Le rendu est
scindé en fonctions **pures** (`rendre_markdown`, `rendre_json`) prenant le dict
assemblé, pour rester testables sans base de données ; `construire_markdown` /
`construire_json` y ajoutent l'accès base.
"""
from __future__ import annotations

import json
from typing import Any

from mvc.services.sequence_pdf import assembler_sequence
from mvc.models.element_seance_model import TYPE_LABELS

# Champs institutionnels de la séquence (SEQ-02), avec leur libellé.
_CADRE: tuple[tuple[str, str], ...] = (
    ("Prerequis", "Prérequis"),
    ("PositionnementProgression", "Positionnement dans la progression"),
    ("DureeEstimee", "Durée estimée"),
    ("ModalitesEvaluation", "Modalités d'évaluation"),
)

# Champs d'une séance affichés dans l'export (colonne -> libellé), dans l'ordre.
_SEANCE: tuple[tuple[str, str], ...] = (
    ("Theme", "Thème"),
    ("ObjectifOperationnel", "Objectif opérationnel"),
    ("ConsigneGenerale", "Consigne générale"),
    ("ModalitePedagogique", "Modalité pédagogique"),
    ("ConditionRealisation", "Conditions de réalisation"),
    ("ConditionValidation", "Conditions de validation"),
    ("Remediation", "Remédiation"),
    ("ProductionAttendue", "Production attendue"),
)


def _export_dict(data: dict[str, Any]) -> dict[str, Any]:
    """Structure d'export neutre, commune au JSON et au Markdown."""
    sequence: dict[str, Any] = data["sequence"]
    connaissances: list[dict[str, Any]] = data.get("connaissances", [])
    savoirs_libres: list[str] = data.get("savoirs_libres", [])
    seances: list[dict[str, Any]] = data.get("seances", [])
    return {
        "titre": sequence.get("Titre"),
        "niveau": sequence.get("niveau_classe_id_label"),
        "cadre": [
            {"libelle": libelle, "valeur": str(sequence[col])}
            for col, libelle in _CADRE
            if sequence.get(col)
        ],
        "connaissances": [
            {
                "code": g.get("code"),
                "intitule": g.get("intitule"),
                "connaissances": [
                    {
                        "libelle": k.get("libelle"),
                        "niveau_officiel": k.get("niveau_officiel"),
                        "niveau_cible": k.get("niveau_cible"),
                        "statut": k.get("statut"),
                        "statut_label": k.get("statut_label"),
                    }
                    for k in g.get("connaissances", [])
                ],
            }
            for g in connaissances
        ],
        "savoirs_libres": list(savoirs_libres),
        "seances": [
            {
                "ordre": se.get("Ordre"),
                "titre": se.get("Titre"),
                "duree_minutes": se.get("DureeEstimeeMinutes"),
                "champs": [
                    {"libelle": libelle, "valeur": str(se[col])}
                    for col, libelle in _SEANCE
                    if se.get(col)
                ],
                "elements": [
                    {
                        "ordre": e.get("Ordre"),
                        "type": TYPE_LABELS.get(str(e.get("Type")), e.get("Type")),
                        "titre": e.get("Titre"),
                        "contenu": e.get("Contenu"),
                        "duree_minutes": e.get("DureeMinutes"),
                        "obligatoire": bool(e.get("Obligatoire")),
                    }
                    for e in se.get("elements", [])
                ],
            }
            for se in seances
        ],
    }


def rendre_json(data: dict[str, Any]) -> str:
    """Sérialise la séquence assemblée en JSON (UTF-8, indenté)."""
    return json.dumps(_export_dict(data), ensure_ascii=False, indent=2) + "\n"


def rendre_markdown(data: dict[str, Any]) -> str:
    """Rend la séquence assemblée en Markdown lisible."""
    e = _export_dict(data)
    out: list[str] = [f"# {e['titre'] or 'Séquence sans titre'}", ""]
    if e["niveau"]:
        out.append(f"*Niveau : {e['niveau']}*")
        out.append("")

    if e["cadre"]:
        out += ["## Cadre institutionnel", ""]
        for c in e["cadre"]:
            out += [f"**{c['libelle']}**", "", str(c["valeur"]), ""]

    if e["connaissances"]:
        out += ["## Savoirs associés", ""]
        for g in e["connaissances"]:
            out.append(f"### {g['code']} — {g['intitule']}")
            out.append("")
            for k in g["connaissances"]:
                details: list[str] = []
                if k["niveau_cible"] is not None:
                    details.append(f"cible {k['niveau_cible']}")
                if k["niveau_officiel"] is not None:
                    details.append(f"officiel {k['niveau_officiel']}")
                if k["statut_label"]:
                    details.append(str(k["statut_label"]))
                suffixe = f" — {', '.join(details)}" if details else ""
                out.append(f"- {k['libelle']}{suffixe}")
            out.append("")
    elif e["savoirs_libres"]:
        out += ["## Savoirs associés", ""]
        for s in e["savoirs_libres"]:
            out.append(f"- {s}")
        out.append("")

    if e["seances"]:
        out += ["## Séances", ""]
        for se in e["seances"]:
            titre = se["titre"] or "Séance"
            duree = f" ({se['duree_minutes']} min)" if se["duree_minutes"] is not None else ""
            out.append(f"### {se['ordre']} — {titre}{duree}")
            out.append("")
            for c in se["champs"]:
                out += [f"**{c['libelle']}**", "", str(c["valeur"]), ""]
            if se["elements"]:
                out += ["**Déroulé :**", ""]
                for el in se["elements"]:
                    d = f" ({el['duree_minutes']} min)" if el["duree_minutes"] is not None else ""
                    opt = "" if el["obligatoire"] else " *(facultatif)*"
                    out.append(f"{el['ordre']}. **{el['type']}** — {el['titre']}{d}{opt}")
                    if el["contenu"]:
                        out.append(f"   {el['contenu']}")
                out.append("")

    return "\n".join(out).rstrip() + "\n"


def construire_json(sequence_id: int) -> str:
    """Export JSON d'une séquence (accès base)."""
    return rendre_json(assembler_sequence(sequence_id))


def construire_markdown(sequence_id: int) -> str:
    """Export Markdown d'une séquence (accès base)."""
    return rendre_markdown(assembler_sequence(sequence_id))
