# pyright: strict
"""Feuille de positionnement — notation d'une séance par critères observés (ADR-032/033).

Réconciliation (ADR-032, décision 7) : l'évaluation est **centrée sur la séance**.
Le professeur, pour chaque **critère observé** de la séance (`seance_critere`) :

- **coche les indicateurs** qu'il observe (`indicateur_observe`, un pivot par
  observation) ; le nombre de coches / total **suggère** un niveau (`suggerer_niveau`) ;
- **positionne** le critère sur la **grille CIEL** (`niveaux_maitrise`) — il retient
  la suggestion ou en décide autrement. Le professeur **arbitre** (décision 6).

Un critère « non observé » n'a pas de ligne `evaluation_critere` (l'élève n'est pas
pénalisé). Tout est persisté au fil de l'eau (feuille HTMX auto-save). Une
observation = une `evaluation_activite` (find-or-create, `activite_id` NULL depuis
la phase C), portant aussi production/preuve, aide apportée et appréciation.

Le `professeur_id` est celui du **compte connecté** lié à une fiche `professeur`
(ADR-022 : l'affectation, qui portait un professeur, a été supprimée).
"""
from __future__ import annotations

from typing import Any

from core.database.db import execute, fetch_all, fetch_one, insert
from core.database.transaction import transaction
from mvc.services.niveaux_maitrise import NIVEAUX, NIVEAUX_POSITIONNABLES, niveau, suggerer_niveau

# Codes réellement stockés (les 4 niveaux positionnables ; « non observé » = pas de ligne).
_POSITIONNABLES: set[str] = {str(n["code"]) for n in NIVEAUX_POSITIONNABLES}


def _contexte(progression_seance_id: int) -> dict[str, Any] | None:
    """Résout la séance-travail : élève, séance, progression et statut."""
    return fetch_one(
        "SELECT pp.Id AS pp_id, pp.progression_sequence_id AS progression_id, pp.Statut AS statut, "
        "pp.seance_id AS seance_id, se.Titre AS seance_titre, e.Nom AS nom, e.Prenom AS prenom "
        "FROM progression_seance pp "
        "JOIN seance se ON se.Id = pp.seance_id "
        "JOIN progression_sequence pe ON pe.Id = pp.progression_sequence_id "
        "JOIN eleve e ON e.Id = pe.eleve_id "
        "WHERE pp.Id = ?",
        (progression_seance_id,),
    )


def professeur_de_user(user_id: int) -> int | None:
    """La fiche professeur rattachée à ce compte, si le compte est lié."""
    row = fetch_one("SELECT Id AS id FROM professeur WHERE UserId = ?", (user_id,))
    return int(row["id"]) if row is not None else None


def _observation(progression_seance_id: int) -> dict[str, Any] | None:
    """L'observation (evaluation_activite) de la séance-travail, si elle existe."""
    return fetch_one(
        "SELECT Id AS id, Appreciation AS appreciation, Production AS production, "
        "AideApportee AS aide FROM evaluation_activite "
        "WHERE progression_seance_id = ? ORDER BY Id LIMIT 1",
        (progression_seance_id,),
    )


def _ensure_observation(progression_seance_id: int, professeur_id: int) -> int:
    """Retourne l'id de l'observation, la créant si absente (activité NULL)."""
    obs = _observation(progression_seance_id)
    if obs is not None:
        return int(obs["id"])
    return insert(
        "INSERT INTO evaluation_activite "
        "(DateEvaluation, progression_seance_id, professeur_id, CreatedAt, UpdatedAt) "
        "VALUES (NOW(), ?, ?, NOW(), NOW())",
        (progression_seance_id, professeur_id),
    )


def _positions(evaluation_activite_id: int) -> dict[int, str]:
    """Niveaux déjà posés, indexés par critère (code CIEL)."""
    rows = fetch_all(
        "SELECT critere_id, Niveau FROM evaluation_critere WHERE evaluation_activite_id = ?",
        (evaluation_activite_id,),
    )
    return {int(r["critere_id"]): str(r["Niveau"]) for r in rows}


def _indicateurs_coches(evaluation_activite_id: int) -> set[int]:
    """Ids des indicateurs cochés (observés) pour cette observation."""
    rows = fetch_all(
        "SELECT indicateur_id FROM indicateur_observe WHERE evaluation_activite_id = ?",
        (evaluation_activite_id,),
    )
    return {int(r["indicateur_id"]) for r in rows}


def indicateurs_du_critere(critere_id: int) -> list[dict[str, Any]]:
    """Indicateurs de réussite d'un critère (id + libellé), dans l'ordre du code."""
    return fetch_all(
        "SELECT Id AS id, Libelle AS libelle FROM indicateur_reussite "
        "WHERE critere_id = ? ORDER BY Code",
        (critere_id,),
    )


def _assembler_critere(
    critere: dict[str, Any], positions: dict[int, str], coches: set[int]
) -> dict[str, Any]:
    """Enrichit un critère observé : indicateurs (+ coché), niveau posé, suggestion."""
    indicateurs = indicateurs_du_critere(int(critere["id"]))
    nb_coches = 0
    for ind in indicateurs:
        ind["coche"] = int(ind["id"]) in coches
        nb_coches += 1 if ind["coche"] else 0
    # Tant qu'aucun indicateur n'est coché, on ne suggère rien : suggérer « Non
    # réalisé » avant toute observation laisserait croire à un échec (le niveau réel
    # reste « non observé »). La suggestion n'apparaît qu'à partir d'un indicateur.
    suggestion = suggerer_niveau(nb_coches, len(indicateurs)) if nb_coches > 0 else "NON_OBSERVE"
    critere["indicateurs"] = indicateurs
    critere["niveau"] = positions.get(int(critere["id"]), "NON_OBSERVE")
    critere["suggestion"] = suggestion
    critere["suggestion_descr"] = niveau(suggestion)
    return critere


def get_grille(progression_seance_id: int) -> dict[str, Any] | None:
    """Feuille de positionnement : compétences **observées** par la séance, leurs
    critères observés (indicateurs cochés, niveau posé, suggestion) et l'observation
    (production/aide/appréciation). None si la progression_seance est introuvable."""
    ctx = _contexte(progression_seance_id)
    if ctx is None:
        return None
    seance_id = int(ctx["seance_id"])
    obs = _observation(progression_seance_id)
    eval_id = int(obs["id"]) if obs is not None else 0
    positions: dict[int, str] = _positions(eval_id) if eval_id else {}
    coches: set[int] = _indicateurs_coches(eval_id) if eval_id else set()

    competences = fetch_all(
        "SELECT sc.competence_id AS id, cp.Code AS code, cp.Intitule AS intitule, sc.Role AS role "
        "FROM seance_competence sc JOIN competence cp ON cp.Id = sc.competence_id "
        "WHERE sc.seance_id = ? ORDER BY cp.Code",
        (seance_id,),
    )
    for comp in competences:
        criteres = fetch_all(
            "SELECT c.Id AS id, c.Code AS code, c.Libelle AS libelle, c.SavoirEtre AS savoir_etre "
            "FROM seance_critere sk JOIN critere_observable c ON c.Id = sk.critere_observable_id "
            "WHERE sk.seance_id = ? AND c.competence_id = ? ORDER BY c.Code",
            (seance_id, comp["id"]),
        )
        comp["criteres"] = [_assembler_critere(cr, positions, coches) for cr in criteres]

    return {
        "progression_seance_id": progression_seance_id,
        "progression_id": ctx["progression_id"],
        "seance_titre": ctx["seance_titre"],
        "statut": ctx["statut"],
        "eleve": f"{ctx['prenom']} {ctx['nom']}",
        "niveaux": NIVEAUX,  # « non observé » + 4 niveaux, pour les puces
        "appreciation": obs["appreciation"] if obs is not None else None,
        "production": obs["production"] if obs is not None else None,
        "aide": obs["aide"] if obs is not None else None,
        "competences": competences,
    }


def contexte_critere(progression_seance_id: int, critere_id: int) -> dict[str, Any] | None:
    """Données d'un seul critère observé (pour re-rendre son fragment HTMX). None si
    le critère n'est pas observé par la séance."""
    ctx = _contexte(progression_seance_id)
    if ctx is None:
        return None
    critere = fetch_one(
        "SELECT c.Id AS id, c.Code AS code, c.Libelle AS libelle, c.SavoirEtre AS savoir_etre "
        "FROM seance_critere sk JOIN critere_observable c ON c.Id = sk.critere_observable_id "
        "WHERE sk.seance_id = ? AND c.Id = ?",
        (ctx["seance_id"], critere_id),
    )
    if critere is None:
        return None
    obs = _observation(progression_seance_id)
    eval_id = int(obs["id"]) if obs is not None else 0
    positions: dict[int, str] = _positions(eval_id) if eval_id else {}
    coches: set[int] = _indicateurs_coches(eval_id) if eval_id else set()
    return _assembler_critere(critere, positions, coches)


def positionner_niveau(
    progression_seance_id: int, professeur_id: int, critere_id: int, niveau_code: str
) -> None:
    """Positionne (ou repositionne) un critère. `NON_OBSERVE` / hors échelle efface
    la ligne (retour à « non observé »). Crée l'observation au besoin."""
    eval_id = _ensure_observation(progression_seance_id, professeur_id)
    if niveau_code in _POSITIONNABLES:
        existe = fetch_one(
            "SELECT Id AS id FROM evaluation_critere WHERE evaluation_activite_id = ? AND critere_id = ?",
            (eval_id, critere_id),
        )
        if existe is not None:
            execute(
                "UPDATE evaluation_critere SET Niveau = ?, UpdatedAt = NOW() WHERE Id = ?",
                (niveau_code, existe["id"]),
            )
        else:
            insert(
                "INSERT INTO evaluation_critere (Niveau, evaluation_activite_id, critere_id, CreatedAt, UpdatedAt) "
                "VALUES (?, ?, ?, NOW(), NOW())",
                (niveau_code, eval_id, critere_id),
            )
    else:
        execute(
            "DELETE FROM evaluation_critere WHERE evaluation_activite_id = ? AND critere_id = ?",
            (eval_id, critere_id),
        )


def maj_indicateurs_observes(
    progression_seance_id: int, professeur_id: int, critere_id: int, coches: set[int]
) -> None:
    """Met à jour les indicateurs cochés d'un critère : coche `coches`, décoche le
    reste (limité aux indicateurs de ce critère). Crée l'observation au besoin."""
    eval_id = _ensure_observation(progression_seance_id, professeur_id)
    indicateurs = {int(i["id"]) for i in indicateurs_du_critere(critere_id)}
    voulus = coches & indicateurs
    with transaction() as tx:
        for ind_id in indicateurs:
            if ind_id in voulus:
                execute(
                    "INSERT INTO indicateur_observe (evaluation_activite_id, indicateur_id, CreatedAt, UpdatedAt) "
                    "VALUES (?, ?, NOW(), NOW()) ON DUPLICATE KEY UPDATE UpdatedAt = NOW()",
                    (eval_id, ind_id),
                    tx=tx,
                )
            else:
                execute(
                    "DELETE FROM indicateur_observe WHERE evaluation_activite_id = ? AND indicateur_id = ?",
                    (eval_id, ind_id),
                    tx=tx,
                )


def enregistrer_notes(
    progression_seance_id: int, professeur_id: int, production: str | None,
    aide: str | None, appreciation: str | None,
) -> None:
    """Enregistre production/preuve, aide apportée et appréciation de l'observation."""
    eval_id = _ensure_observation(progression_seance_id, professeur_id)
    execute(
        "UPDATE evaluation_activite SET Production = ?, AideApportee = ?, Appreciation = ?, "
        "UpdatedAt = NOW() WHERE Id = ?",
        (production, aide, appreciation, eval_id),
    )
