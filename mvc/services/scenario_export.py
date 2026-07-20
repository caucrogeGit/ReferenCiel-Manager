# pyright: strict
"""Export d'un scénario finalisé en **Markdown** et **JSON** (à côté du PDF, ADR-024).

Réutilise l'assemblage commun de `scenario_pdf.assembler_scenario`. Le rendu est
scindé en fonctions **pures** (`rendre_markdown`, `rendre_json`) prenant le dict
assemblé, pour rester testables sans base de données ; `construire_markdown` /
`construire_json` y ajoutent l'accès base.
"""
from __future__ import annotations

import json
from typing import Any

from mvc.services.scenario_pdf import assembler_scenario

_STATUTS = {"brouillon": "Brouillon", "finalise": "Finalisé", "utilise": "Utilisé"}


def _export_dict(data: dict[str, Any]) -> dict[str, Any]:
    """Structure d'export neutre, commune au JSON et au Markdown."""
    scenario: dict[str, Any] = data["scenario"]
    referentiel: "dict[str, Any] | None" = data.get("referentiel")
    activites: list[dict[str, Any]] = data.get("activites", [])
    contexte: list[dict[str, Any]] = data.get("contexte", [])
    connaissances: list[dict[str, Any]] = data.get("connaissances", [])
    savoirs_libres: list[str] = data.get("savoirs_libres", [])
    ressources: list[dict[str, Any]] = data.get("ressources", [])
    return {
        "titre": scenario.get("Titre"),
        "statut": scenario.get("Statut"),
        "intention": scenario.get("Intention"),
        "objectifs": scenario.get("Objectifs"),
        "co_intervention": bool(scenario.get("CoIntervention")),
        "co_auteurs": list(data.get("co_auteurs", [])),
        "referentiel": (
            {"identifiant": referentiel.get("Identifiant"),
             "formation": referentiel.get("formation_intitule")}
            if referentiel else None
        ),
        "contexte": [{"libelle": c["libelle"], "valeur": c["valeur"]} for c in contexte],
        "activites": [
            {
                "code": a.get("code"),
                "intitule": a.get("intitule"),
                "pole": a.get("pole"),
                "competences": [
                    {
                        "code": comp.get("code"),
                        "intitule": comp.get("intitule"),
                        "criteres": [
                            {
                                "libelle": cr.get("libelle"),
                                "savoir_etre": bool(cr.get("savoir_etre")),
                                "indicateurs": list(cr.get("indicateurs", [])),
                            }
                            for cr in comp.get("criteres", [])
                        ],
                    }
                    for comp in a.get("competences", [])
                ],
            }
            for a in activites
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
        "ressources": [
            {"nom": r.get("NomOriginal"), "type": r.get("MimeType"), "taille": r.get("Taille")}
            for r in ressources
        ],
    }


def rendre_json(data: dict[str, Any]) -> str:
    """Sérialise le scénario assemblé en JSON (UTF-8, indenté)."""
    return json.dumps(_export_dict(data), ensure_ascii=False, indent=2) + "\n"


def rendre_markdown(data: dict[str, Any]) -> str:
    """Rend le scénario assemblé en Markdown lisible."""
    e = _export_dict(data)
    out: list[str] = [f"# {e['titre'] or 'Scénario sans titre'}", ""]
    out.append(f"*Statut : {_STATUTS.get(str(e['statut']), str(e['statut'] or '—'))}*")
    if e["referentiel"]:
        ref = e["referentiel"]
        out.append(f"*Référentiel : {ref['formation'] or ''} · {ref['identifiant']}*")
    if e["co_intervention"]:
        out.append(f"*Co-intervention : {', '.join(e['co_auteurs']) or '—'}*")
    out.append("")

    if e["intention"]:
        out += ["## Intention", "", str(e["intention"]), ""]
    if e["objectifs"]:
        out += ["## Objectifs", "", str(e["objectifs"]), ""]
    if e["contexte"]:
        out += ["## Contexte", ""]
        for c in e["contexte"]:
            out += [f"**{c['libelle']}**", "", str(c["valeur"]), ""]
    if e["activites"]:
        out += ["## Liaison au référentiel", ""]
        for a in e["activites"]:
            out.append(f"### {a['code']} — {a['intitule']}")
            if a["pole"]:
                out.append(f"*Pôle : {a['pole']}*")
            out.append("")
            for comp in a["competences"]:
                out.append(f"- **{comp['code']}** {comp['intitule']}")
                for cr in comp["criteres"]:
                    marque = " *(savoir-être)*" if cr["savoir_etre"] else ""
                    out.append(f"  - {cr['libelle']}{marque}")
                    for ind in cr["indicateurs"]:
                        out.append(f"    - ✓ {ind}")
            out.append("")
    if e["connaissances"]:
        out += ["## Connaissances associées", ""]
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
    if e["savoirs_libres"]:
        out += ["## Savoirs associés", ""]
        for s in e["savoirs_libres"]:
            out.append(f"- {s}")
        out.append("")
    if e["ressources"]:
        out += ["## Ressources", ""]
        for r in e["ressources"]:
            out.append(f"- {r['nom']}" + (f" ({r['type']})" if r["type"] else ""))
        out.append("")

    return "\n".join(out).rstrip() + "\n"


def construire_json(scenario_id: int) -> str:
    """Export JSON d'un scénario (accès base)."""
    return rendre_json(assembler_scenario(scenario_id))


def construire_markdown(scenario_id: int) -> str:
    """Export Markdown d'un scénario (accès base)."""
    return rendre_markdown(assembler_scenario(scenario_id))
