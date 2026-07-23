"""Lien Séance ↔ Connaissance (ADR-037, descend l'ADR-028 d'un cran).

La SÉANCE porte les savoirs associés : elle retient des connaissances du
référentiel de son scénario appairé (via sa séquence), avec un niveau cible et
un statut dans la progression. La séquence n'en fait plus qu'une SYNTHÈSE
dérivée. Écriture ciblée d'un seul lien par requête (motif des pivots HTMX).
"""

from datetime import datetime, timezone

from core.database.db import fetch_all, fetch_one, execute, insert
from mvc.models.sequence_connaissance_model import (
    STATUTS,
    STATUT_LABELS,
    NIVEAUX_TAXONOMIE,
    get_arbre_connaissances,
)

__all__ = [
    "STATUTS", "STATUT_LABELS", "NIVEAUX_TAXONOMIE", "get_arbre_connaissances",
    "get_liens_by_seance", "lier", "delier", "maj_niveau_cible", "maj_statut",
    "referentiel_et_scenario_de_seance", "competences_retenues_au_scenario_de_seance",
    "competence_de_connaissance", "savoirs_par_seance_de_sequence",
    "nb_seances_ouvrantes",
]


def get_liens_by_seance(seance_id):
    """Liens de la séance, indexés par connaissance_id."""
    rows = fetch_all(
        "SELECT Id, connaissance_id, NiveauCible, Statut, Commentaire "
        "FROM seance_connaissance WHERE seance_id = ?",
        (seance_id,),
    )
    return {int(r["connaissance_id"]): r for r in rows}


def lier(seance_id, connaissance_id):
    """Retient une connaissance pour la séance (sans niveau ni statut)."""
    if fetch_one(
        "SELECT 1 AS x FROM seance_connaissance WHERE seance_id = ? AND connaissance_id = ? LIMIT 1",
        (seance_id, connaissance_id),
    ) is not None:
        return
    now = datetime.now(timezone.utc)
    insert(
        "INSERT INTO seance_connaissance (seance_id, connaissance_id, CreatedAt, UpdatedAt) "
        "VALUES (?, ?, ?, ?)",
        (seance_id, connaissance_id, now, now),
    )


def delier(seance_id, connaissance_id):
    execute(
        "DELETE FROM seance_connaissance WHERE seance_id = ? AND connaissance_id = ?",
        (seance_id, connaissance_id),
    )


def maj_niveau_cible(seance_id, connaissance_id, niveau):
    execute(
        "UPDATE seance_connaissance SET NiveauCible = ?, UpdatedAt = ? "
        "WHERE seance_id = ? AND connaissance_id = ?",
        (niveau, datetime.now(timezone.utc), seance_id, connaissance_id),
    )


def maj_statut(seance_id, connaissance_id, statut):
    execute(
        "UPDATE seance_connaissance SET Statut = ?, UpdatedAt = ? "
        "WHERE seance_id = ? AND connaissance_id = ?",
        (statut, datetime.now(timezone.utc), seance_id, connaissance_id),
    )


def referentiel_et_scenario_de_seance(seance_id):
    """(referentiel_id, scenario_id, nature de la séquence) de la séance, via
    sa séquence et le scénario appairé — (None, None, 'formative') à défaut."""
    row = fetch_one(
        "SELECT sc.referentiel_id AS ref, sc.Id AS scen, sq.Nature AS nature "
        "FROM seance se "
        "JOIN sequence sq ON sq.Id = se.sequence_id "
        "LEFT JOIN scenario_sequence ss ON ss.sequence_id = sq.Id "
        "LEFT JOIN scenario sc ON sc.Id = ss.scenario_id "
        "WHERE se.Id = ?",
        (seance_id,),
    )
    if row is None:
        return None, None, "formative"
    return row["ref"], row["scen"], str(row["nature"] or "formative")


def competences_retenues_au_scenario_de_seance(seance_id):
    """Compétences retenues (critères cochés) au scénario de la séance : le
    SCÉNARIO reste la source canonique (ADR-036), un cran plus bas (ADR-037)."""
    _ref, scenario_id, _n = referentiel_et_scenario_de_seance(seance_id)
    if scenario_id is None:
        return set()
    rows = fetch_all(
        "SELECT DISTINCT c.competence_id AS comp FROM scenario_critere sc "
        "JOIN critere_observable c ON c.Id = sc.critere_observable_id "
        "WHERE sc.scenario_id = ?",
        (scenario_id,),
    )
    return {int(r["comp"]) for r in rows}


def competence_de_connaissance(connaissance_id):
    """Compétence porteuse d'une connaissance, ou None."""
    row = fetch_one("SELECT competence_id FROM connaissance WHERE Id = ?", (connaissance_id,))
    return int(row["competence_id"]) if row else None


def savoirs_par_seance_de_sequence(sequence_id):
    """Synthèse DÉRIVÉE pour la séquence (ADR-037) : les savoirs de ses séances,
    avec compétence, séance d'origine, niveau cible et statut — dans l'ordre."""
    return fetch_all(
        "SELECT se.Ordre AS seance_ordre, se.Titre AS seance_titre, "
        "cp.Code AS competence_code, cp.Intitule AS competence_intitule, "
        "k.Libelle AS savoir, sk.NiveauCible, sk.Statut "
        "FROM seance_connaissance sk "
        "JOIN seance se ON se.Id = sk.seance_id "
        "JOIN connaissance k ON k.Id = sk.connaissance_id "
        "JOIN competence cp ON cp.Id = k.competence_id "
        "WHERE se.sequence_id = ? "
        "ORDER BY cp.Code, se.Ordre, k.Id",
        (sequence_id,),
    )


def nb_seances_ouvrantes(sequence_id, statuts_ouvrants):
    """Nombre de séances de la séquence ayant AU MOINS UN savoir ouvrant
    (validé : niveau + statut, et statut ouvrant pour la nature) — c'est la
    condition de PUBLICATION de la séquence (ADR-037)."""
    if not statuts_ouvrants:
        return 0
    marqueurs = ", ".join("?" for _ in statuts_ouvrants)
    row = fetch_one(
        "SELECT COUNT(DISTINCT sk.seance_id) AS n FROM seance_connaissance sk "
        "JOIN seance se ON se.Id = sk.seance_id "
        "WHERE se.sequence_id = ? AND sk.NiveauCible IS NOT NULL "
        "AND sk.Statut IN (" + marqueurs + ")",
        (sequence_id, *statuts_ouvrants),
    )
    return int(row["n"]) if row else 0


def get_connaissances_retenues_agregees(sequence_id, ref_id):
    """Agrégat pour les exports de la séquence (ADR-037) : même forme que
    l'ancien `get_connaissances_retenues`, dérivée des savoirs des séances —
    niveau cible retenu = le plus haut, statuts = libellés distincts."""
    arbre = get_arbre_connaissances(ref_id)
    lignes = fetch_all(
        "SELECT sk.connaissance_id AS kid, MAX(sk.NiveauCible) AS niveau, "
        "GROUP_CONCAT(DISTINCT sk.Statut ORDER BY sk.Statut) AS statuts "
        "FROM seance_connaissance sk JOIN seance se ON se.Id = sk.seance_id "
        "WHERE se.sequence_id = ? GROUP BY sk.connaissance_id",
        (sequence_id,),
    )
    par_k = {int(r["kid"]): r for r in lignes}
    groupes = []
    for comp in arbre:
        retenues = []
        for k in comp.get("connaissances", []):
            r = par_k.get(int(k["Id"]))
            if r is None:
                continue
            statuts = [s for s in (r["statuts"] or "").split(",") if s]
            retenues.append({
                "libelle": k["Libelle"],
                "niveau_officiel": k.get("NiveauTaxonomique"),
                "niveau_cible": r["niveau"],
                "statut": statuts[0] if statuts else None,
                "statut_label": " / ".join(STATUT_LABELS.get(s, s) for s in statuts) or None,
            })
        if retenues:
            groupes.append({"code": comp["Code"], "intitule": comp["Intitule"], "connaissances": retenues})
    return groupes
