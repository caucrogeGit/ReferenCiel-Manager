# pyright: strict
"""Espace élève v2 — cocher la checklist d'un palier (écriture, appartenance).

L'élève auto-déclare les items faits (`item_coche.CocheEleve`) sur un de **ses**
paliers. La **validation** reste au professeur (`item_coche.CocheProfesseur`, non
touché ici) : cocher côté élève ne change donc pas le statut du palier. Sécurité
row-level vérifiée à chaque appel (le palier doit appartenir au compte). Upsert
idempotent via la clé unique `(item_id, progression_palier_id)`.
"""
from __future__ import annotations

from typing import Any

from core.database.db import execute, fetch_all, fetch_one
from core.database.transaction import transaction


def _palier_de_l_eleve(progression_palier_id: int, user_id: int) -> dict[str, Any] | None:
    return fetch_one(
        "SELECT pp.Id AS progression_palier_id, pp.seance_id AS seance_id, pa.Titre AS palier_titre "
        "FROM progression_palier pp "
        "JOIN progression_parcours pe ON pe.Id = pp.progression_parcours_id "
        "JOIN eleve e ON e.Id = pe.eleve_id "
        "JOIN seance pa ON pa.Id = pp.seance_id "
        "WHERE pp.Id = ? AND e.UserId = ?",
        (progression_palier_id, user_id),
    )


def _checklist_du_palier(seance_id: int) -> dict[str, Any] | None:
    return fetch_one(
        "SELECT Id AS id FROM checklist WHERE seance_id = ? ORDER BY Id LIMIT 1", (seance_id,)
    )


def get_checklist(progression_palier_id: int, user_id: int) -> dict[str, Any] | None:
    """Checklist du palier (sections → items + état coché de l'élève) si elle lui appartient."""
    palier = _palier_de_l_eleve(progression_palier_id, user_id)
    if palier is None:
        return None
    checklist = _checklist_du_palier(int(palier["seance_id"]))
    if checklist is None:
        return None
    sections = fetch_all(
        "SELECT Id AS id, Titre AS titre FROM section_checklist WHERE checklist_id = ? ORDER BY Id",
        (checklist["id"],),
    )
    for section in sections:
        section["items"] = fetch_all(
            "SELECT i.Id AS id, i.Libelle AS libelle, "
            "COALESCE(ic.CocheEleve, 0) AS coche_eleve "
            "FROM item_checklist i "
            "LEFT JOIN item_coche ic "
            "  ON ic.item_id = i.Id AND ic.progression_palier_id = ? "
            "WHERE i.section_id = ? ORDER BY i.Id",
            (progression_palier_id, section["id"]),
        )
    return {
        "progression_palier_id": progression_palier_id,
        "palier_titre": palier["palier_titre"],
        "checklist_id": checklist["id"],
        "sections": sections,
    }


def enregistrer_coches(
    progression_palier_id: int, user_id: int, items_coches: set[int]
) -> dict[str, Any] | None:
    """Enregistre l'auto-cochage de l'élève sur TOUS les items de la checklist.

    `items_coches` : ids d'items cochés. Les autres sont remis à 0. Upsert sur la
    clé `(item_id, progression_palier_id)`, sans jamais toucher `CocheProfesseur`.
    Renvoie {items, coches} ou None si le palier n'appartient pas au compte.
    """
    palier = _palier_de_l_eleve(progression_palier_id, user_id)
    if palier is None:
        return None
    checklist = _checklist_du_palier(int(palier["seance_id"]))
    if checklist is None:
        return None

    items = fetch_all(
        "SELECT i.Id AS id FROM item_checklist i "
        "JOIN section_checklist s ON s.Id = i.section_id "
        "WHERE s.checklist_id = ?",
        (checklist["id"],),
    )
    ids = {int(it["id"]) for it in items}
    coches = ids & items_coches

    with transaction() as tx:
        for iid in ids:
            execute(
                "INSERT INTO item_coche "
                "(CocheEleve, CocheProfesseur, item_id, progression_palier_id, CreatedAt, UpdatedAt) "
                "VALUES (?, 0, ?, ?, NOW(), NOW()) "
                "ON DUPLICATE KEY UPDATE CocheEleve = VALUES(CocheEleve), UpdatedAt = NOW()",
                (1 if iid in items_coches else 0, iid, progression_palier_id),
                tx=tx,
            )
    return {"items": len(ids), "coches": len(coches)}
