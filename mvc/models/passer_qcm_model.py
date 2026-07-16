# pyright: strict
"""Espace élève v2 — passer un QCM (écriture avec contrôle d'appartenance).

L'élève **connecté** répond au QCM d'un de **ses** paliers ; on fige la justesse
de chaque réponse, on calcule le score (%), on enregistre la tentative et on met
à jour le statut du palier (100 % → validé, sinon en cours ; un palier déjà validé
ne régresse jamais). La sécurité **row-level** est vérifiée à chaque appel :
le `progression_palier` doit appartenir à l'élève du compte (`eleve.UserId`).
Tentatives multiples : chaque envoi crée une nouvelle `tentative_qcm`.
"""
from __future__ import annotations

from typing import Any

from core.database.db import execute, fetch_all, fetch_one, insert
from core.database.transaction import transaction

_STATUT_VALIDE = "valide"
_STATUT_EN_COURS = "en_cours"


def _palier_de_l_eleve(progression_palier_id: int, user_id: int) -> dict[str, Any] | None:
    """Le palier de progression s'il appartient bien au compte (sécurité row-level)."""
    return fetch_one(
        "SELECT pp.Id AS progression_palier_id, pp.seance_id AS seance_id, pa.Titre AS palier_titre "
        "FROM progression_palier pp "
        "JOIN progression_parcours pe ON pe.Id = pp.progression_parcours_id "
        "JOIN eleve e ON e.Id = pe.eleve_id "
        "JOIN seance pa ON pa.Id = pp.seance_id "
        "WHERE pp.Id = ? AND e.UserId = ?",
        (progression_palier_id, user_id),
    )


def _qcm_du_palier(seance_id: int) -> dict[str, Any] | None:
    return fetch_one(
        "SELECT Id AS id FROM qcm WHERE seance_id = ? ORDER BY Id LIMIT 1", (seance_id,)
    )


def get_qcm_a_passer(progression_palier_id: int, user_id: int) -> dict[str, Any] | None:
    """QCM du palier (questions + choix) si le palier appartient au compte.

    None si le palier n'est pas à cet élève, ou si le palier n'a pas de QCM.
    N'expose PAS la bonne réponse (le corrigé reste côté serveur).
    """
    palier = _palier_de_l_eleve(progression_palier_id, user_id)
    if palier is None:
        return None
    qcm = _qcm_du_palier(int(palier["seance_id"]))
    if qcm is None:
        return None
    questions = fetch_all(
        "SELECT Id AS id, Numero AS numero, Enonce AS enonce "
        "FROM question_qcm WHERE qcm_id = ? ORDER BY Numero",
        (qcm["id"],),
    )
    for question in questions:
        question["choix"] = fetch_all(
            "SELECT Id AS id, Lettre AS lettre, Texte AS texte "
            "FROM choix_qcm WHERE question_id = ? ORDER BY Lettre",
            (question["id"],),
        )
    return {
        "progression_palier_id": progression_palier_id,
        "palier_titre": palier["palier_titre"],
        "qcm_id": qcm["id"],
        "questions": questions,
    }


def _prochain_numero(progression_palier_id: int) -> int:
    row = fetch_one(
        "SELECT COALESCE(MAX(NumeroTentative), 0) AS n "
        "FROM tentative_qcm WHERE progression_palier_id = ?",
        (progression_palier_id,),
    )
    return (int(row["n"]) + 1) if row is not None else 1


def enregistrer_tentative(
    progression_palier_id: int, user_id: int, reponses: dict[int, int]
) -> dict[str, Any] | None:
    """Enregistre une tentative (transactionnelle) et met à jour le statut du palier.

    `reponses` : {question_id: choix_id choisi}. Renvoie {score, total, validee,
    numero} ou None si le palier n'appartient pas au compte / n'a pas de QCM.
    """
    palier = _palier_de_l_eleve(progression_palier_id, user_id)
    if palier is None:
        return None
    qcm = _qcm_du_palier(int(palier["seance_id"]))
    if qcm is None:
        return None

    questions = fetch_all(
        "SELECT Id AS id, BonneReponse AS bonne FROM question_qcm WHERE qcm_id = ?",
        (qcm["id"],),
    )
    total = len(questions)

    # Correction côté serveur : la lettre du choix retenu doit égaler la bonne réponse.
    corriges: list[tuple[int, int, bool]] = []  # (question_id, choix_id, est_correcte)
    corrects = 0
    for question in questions:
        qid = int(question["id"])
        choix_id = reponses.get(qid)
        if choix_id is None:
            continue  # non répondue → comptée fausse (aucune réponse enregistrée)
        choix = fetch_one(
            "SELECT Lettre AS lettre FROM choix_qcm WHERE Id = ? AND question_id = ?",
            (choix_id, qid),
        )
        est_correcte = choix is not None and str(choix["lettre"]) == str(question["bonne"])
        if est_correcte:
            corrects += 1
        corriges.append((qid, choix_id, est_correcte))

    score = round(100 * corrects / total) if total > 0 else 0
    validee = total > 0 and corrects == total
    numero = _prochain_numero(progression_palier_id)

    with transaction() as tx:
        tentative_id = insert(
            "INSERT INTO tentative_qcm "
            "(NumeroTentative, Score, Validee, DateTentative, progression_palier_id, CreatedAt, UpdatedAt) "
            "VALUES (?, ?, ?, NOW(), ?, NOW(), NOW())",
            (numero, score, 1 if validee else 0, progression_palier_id),
            tx=tx,
        )
        for qid, choix_id, est_correcte in corriges:
            execute(
                "INSERT INTO reponse_qcm "
                "(EstCorrecte, tentative_id, question_id, choix_id, CreatedAt, UpdatedAt) "
                "VALUES (?, ?, ?, ?, NOW(), NOW())",
                (1 if est_correcte else 0, tentative_id, qid, choix_id),
                tx=tx,
            )
        # 100 % → validé ; sinon en cours. Un palier déjà validé ne régresse pas.
        nouveau_statut = _STATUT_VALIDE if validee else _STATUT_EN_COURS
        execute(
            "UPDATE progression_palier SET Statut = ? WHERE Id = ? AND Statut <> ?",
            (nouveau_statut, progression_palier_id, _STATUT_VALIDE),
            tx=tx,
        )

    return {"score": score, "total": total, "validee": validee, "numero": numero}
