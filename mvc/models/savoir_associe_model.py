"""Accès aux savoirs associés d'une séquence (liste libre, SEQ-02).

Un savoir associé est un simple libellé rattaché à une séquence. Il ne dépend
d'aucun référentiel : c'est une liste ouverte que le professeur enrichit.
"""

from datetime import datetime, timezone

from core.database.db import fetch_all, fetch_one, execute, insert

SELECT_BY_SEQUENCE = "SELECT Id, Libelle, sequence_id FROM savoir_associe WHERE sequence_id = ? ORDER BY Id"
SELECT_BY_ID       = "SELECT Id, Libelle, sequence_id FROM savoir_associe WHERE Id = ?"
INSERT             = "INSERT INTO savoir_associe (Libelle, sequence_id, CreatedAt, UpdatedAt) VALUES (?, ?, ?, ?)"
DELETE             = "DELETE FROM savoir_associe WHERE Id = ?"


def get_savoirs_by_sequence(sequence_id):
    return fetch_all(SELECT_BY_SEQUENCE, (sequence_id,))


def get_savoir_by_id(id):
    return fetch_one(SELECT_BY_ID, (id,))


def add_savoir(sequence_id, libelle):
    now = datetime.now(timezone.utc)
    return insert(INSERT, (libelle, sequence_id, now, now))


def delete_savoir(id):
    execute(DELETE, (id,))
