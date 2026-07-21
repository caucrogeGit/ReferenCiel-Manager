# pyright: strict
"""Feuille de positionnement — notation d'une séance par critères observés (ADR-032/033).

Réconciliation (ADR-032, décision 7) : l'évaluation est **centrée sur la séance**,
non plus sur l'activité. Le professeur positionne chaque **critère observé** de la
séance (`seance_critere`) à un niveau de la **grille officielle CIEL**
(`niveaux_maitrise`). Un critère laissé « non observé » ne pénalise pas l'élève :
il n'a simplement pas de ligne d'évaluation.

Une observation = une `evaluation_activite` (find-or-create, rattachée à la
`progression_seance`, `activite_id` NULL depuis la phase C) + N `evaluation_critere`
(upsert explicite : la table n'a pas de clé unique). Elle porte aussi la
production/preuve, l'aide apportée et l'appréciation. Le professeur **arbitre** :
le nombre d'indicateurs ne fait que **suggérer** (ADR-032). SQL visible et paramétré.

Le `professeur_id` est celui du **compte connecté** lié à une fiche `professeur`
(ADR-022 : l'affectation, qui portait un professeur, a été supprimée).
"""
from __future__ import annotations

from typing import Any

from core.database.db import execute, fetch_all, fetch_one, insert
from core.database.transaction import transaction
from mvc.services.niveaux_maitrise import NIVEAUX, NIVEAUX_POSITIONNABLES

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


def _positions(evaluation_activite_id: int) -> dict[int, str]:
    """Niveaux déjà posés, indexés par critère (code CIEL)."""
    rows = fetch_all(
        "SELECT critere_id, Niveau FROM evaluation_critere WHERE evaluation_activite_id = ?",
        (evaluation_activite_id,),
    )
    return {int(r["critere_id"]): str(r["Niveau"]) for r in rows}


def get_grille(progression_seance_id: int) -> dict[str, Any] | None:
    """Feuille de positionnement : compétences **observées** par la séance, leurs
    critères observés (+ indicateurs, + niveau déjà posé) et l'observation
    (production/aide/appréciation). None si la progression_seance est introuvable.

    À la différence de l'ancienne grille (activité-centrée, tout le référentiel),
    on ne montre que ce que la séance **observe** (`seance_competence`/`seance_critere`),
    et aucune activité n'est requise (ADR-032, décision 7)."""
    ctx = _contexte(progression_seance_id)
    if ctx is None:
        return None
    seance_id = int(ctx["seance_id"])
    obs = _observation(progression_seance_id)
    positions = _positions(int(obs["id"])) if obs is not None else {}

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
        for cr in criteres:
            cr["indicateurs"] = fetch_all(
                "SELECT Id AS id, Libelle AS libelle FROM indicateur_reussite "
                "WHERE critere_id = ? ORDER BY Code",
                (cr["id"],),
            )
            cr["niveau"] = positions.get(int(cr["id"]), "NON_OBSERVE")
        comp["criteres"] = criteres

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


def enregistrer_notation(
    progression_seance_id: int,
    niveaux: dict[int, str],
    user_id: int | None = None,
    *,
    production: str | None = None,
    aide: str | None = None,
    appreciation: str | None = None,
) -> dict[str, Any] | None:
    """Enregistre le positionnement des critères + l'observation (find-or-create).

    `niveaux` : {critere_id: code}. Un code CIEL positionnable (`NIVEAU_1..4`) est
    upserté ; `NON_OBSERVE` (ou tout code hors échelle) **efface** la ligne du
    critère (retour à « non observé »). Sans professeur identifiable (compte non
    lié à une fiche `professeur`), on n'écrit rien. None si la progression_seance
    est introuvable. Renvoie {notes} = nombre de critères positionnés."""
    ctx = _contexte(progression_seance_id)
    if ctx is None:
        return None
    professeur_id = professeur_de_user(user_id) if user_id is not None else None
    if professeur_id is None:
        return None

    a_poser = {cid: niv for cid, niv in niveaux.items() if niv in _POSITIONNABLES}
    a_effacer = {cid for cid, niv in niveaux.items() if niv not in _POSITIONNABLES}

    with transaction() as tx:
        obs = fetch_one(
            "SELECT Id AS id FROM evaluation_activite WHERE progression_seance_id = ? ORDER BY Id LIMIT 1",
            (progression_seance_id,),
            tx=tx,
        )
        if obs is None:
            eval_id = insert(
                "INSERT INTO evaluation_activite "
                "(DateEvaluation, progression_seance_id, professeur_id, Appreciation, Production, AideApportee, "
                "CreatedAt, UpdatedAt) VALUES (NOW(), ?, ?, ?, ?, ?, NOW(), NOW())",
                (progression_seance_id, professeur_id, appreciation, production, aide),
                tx=tx,
            )
        else:
            eval_id = int(obs["id"])
            execute(
                "UPDATE evaluation_activite SET Appreciation = ?, Production = ?, AideApportee = ?, "
                "UpdatedAt = NOW() WHERE Id = ?",
                (appreciation, production, aide, eval_id),
                tx=tx,
            )
        for critere_id, niv in a_poser.items():
            existe = fetch_one(
                "SELECT Id AS id FROM evaluation_critere WHERE evaluation_activite_id = ? AND critere_id = ?",
                (eval_id, critere_id),
                tx=tx,
            )
            if existe is None:
                insert(
                    "INSERT INTO evaluation_critere (Niveau, evaluation_activite_id, critere_id, CreatedAt, UpdatedAt) "
                    "VALUES (?, ?, ?, NOW(), NOW())",
                    (niv, eval_id, critere_id),
                    tx=tx,
                )
            else:
                execute(
                    "UPDATE evaluation_critere SET Niveau = ?, UpdatedAt = NOW() WHERE Id = ?",
                    (niv, existe["id"]),
                    tx=tx,
                )
        for critere_id in a_effacer:
            execute(
                "DELETE FROM evaluation_critere WHERE evaluation_activite_id = ? AND critere_id = ?",
                (eval_id, critere_id),
                tx=tx,
            )
    return {"notes": len(a_poser)}
