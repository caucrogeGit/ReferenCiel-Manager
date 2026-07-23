"""Attribution d'une séquence aux élèves (ADR-035).

Une attribution = une ligne `progression_sequence` (élève x séquence).
La page Attributions remplace le CRUD « Progressions » du menu Exécution :
attribution par classe entière ou par élève, retrait gardé (les progressions
de séance et les bilans, en RESTRICT au contrat, bloquent le retrait).
"""

from datetime import datetime, timezone

from core.database.db import fetch_all, fetch_one, execute, insert


def attributions(sequence_id):
    """Attributions de la séquence (élève + classe), classées par classe."""
    return fetch_all(
        "SELECT p.Id, p.Statut, e.Nom, e.Prenom, "
        "c.Code AS classe_code, c.Libelle AS classe_libelle "
        "FROM progression_sequence p "
        "JOIN eleve e ON e.Id = p.eleve_id "
        "LEFT JOIN classe c ON c.Id = e.classe_id "
        "WHERE p.sequence_id = ? "
        "ORDER BY (c.Code IS NULL), c.Code, e.Nom, e.Prenom",
        (sequence_id,),
    )


def classes_avec_effectif():
    """Classes et leur effectif, pour l'attribution par classe entière."""
    return fetch_all(
        "SELECT c.Id, c.Code, c.Libelle, COUNT(e.Id) AS nb_eleves "
        "FROM classe c LEFT JOIN eleve e ON e.classe_id = c.Id "
        "GROUP BY c.Id, c.Code, c.Libelle ORDER BY c.Code"
    )


def eleves_non_attribues(sequence_id):
    """Élèves sans progression sur cette séquence, pour l'attribution unitaire."""
    return fetch_all(
        "SELECT e.Id, e.Nom, e.Prenom, c.Code AS classe_code "
        "FROM eleve e LEFT JOIN classe c ON c.Id = e.classe_id "
        "WHERE e.Id NOT IN (SELECT eleve_id FROM progression_sequence WHERE sequence_id = ?) "
        "ORDER BY (c.Code IS NULL), c.Code, e.Nom, e.Prenom",
        (sequence_id,),
    )


def attribuer_eleve(sequence_id, eleve_id):
    """Crée la progression si absente (idempotent). Retourne 1 si créée, 0 sinon."""
    row = fetch_one(
        "SELECT Id FROM progression_sequence WHERE sequence_id = ? AND eleve_id = ?",
        (sequence_id, eleve_id),
    )
    if row is not None:
        return 0
    now = datetime.now(timezone.utc)
    insert(
        "INSERT INTO progression_sequence (Statut, DateDebut, eleve_id, sequence_id, CreatedAt, UpdatedAt) "
        "VALUES ('non_commencee', NULL, ?, ?, ?, ?)",
        (eleve_id, sequence_id, now, now),
    )
    return 1


def attribuer_classe(sequence_id, classe_id):
    """Attribue la séquence à tous les élèves de la classe pas encore attribués.

    Retourne le nombre de progressions créées (les existantes sont conservées).
    """
    eleves = fetch_all("SELECT Id FROM eleve WHERE classe_id = ?", (classe_id,))
    return sum(attribuer_eleve(sequence_id, int(e["Id"])) for e in eleves)


def motif_blocage_retrait(progression_id):
    """Raison humaine empêchant le retrait (FK restrict), ou None si libre."""
    row = fetch_one(
        "SELECT COUNT(*) AS n FROM progression_seance WHERE progression_sequence_id = ?",
        (progression_id,),
    )
    if row and int(row["n"]) > 0:
        return "des progressions de séance (travail élève commencé)"
    row = fetch_one(
        "SELECT COUNT(*) AS n FROM bilan_eleve WHERE progression_sequence_id = ?",
        (progression_id,),
    )
    if row and int(row["n"]) > 0:
        return "un bilan"
    return None


def retirer(progression_id):
    execute("DELETE FROM progression_sequence WHERE Id = ?", (progression_id,))
