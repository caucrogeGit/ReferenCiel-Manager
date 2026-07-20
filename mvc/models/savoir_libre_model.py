"""Savoirs libres d'une séquence sans référentiel (ADR-030).

Liste de texte libre saisie par le professeur, comme les indicateurs de réussite
du scénario. N'existe que pour les séquences hors référentiel (matières non
adossées) ; avec référentiel, ce sont les connaissances structurées qui priment.
"""

from datetime import datetime, timezone

from core.database.db import fetch_all, fetch_one, execute, insert


def get_savoirs_libres(sequence_id):
    """Savoirs libres d'une séquence, dans l'ordre de saisie."""
    return fetch_all(
        "SELECT Id, Libelle FROM savoir_libre WHERE sequence_id = ? ORDER BY Id",
        (sequence_id,),
    )


def ajouter_savoir_libre(sequence_id, libelle):
    now = datetime.now(timezone.utc)
    return insert(
        "INSERT INTO savoir_libre (Libelle, sequence_id, CreatedAt, UpdatedAt) VALUES (?, ?, ?, ?)",
        (libelle, sequence_id, now, now),
    )


def get_savoir_libre(savoir_id):
    return fetch_one("SELECT Id, sequence_id FROM savoir_libre WHERE Id = ?", (savoir_id,))


def supprimer_savoir_libre(savoir_id):
    execute("DELETE FROM savoir_libre WHERE Id = ?", (savoir_id,))
