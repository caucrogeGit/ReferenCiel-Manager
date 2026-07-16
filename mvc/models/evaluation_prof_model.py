# pyright: strict
"""Évaluation professeur — boucler la progression d'un élève.

Vue de détail d'une progression (les seances de l'élève + les preuves : meilleur
score QCM, cochage élève/prof, nombre de dépôts), puis deux écritures du
professeur : **valider une séance** (`progression_palier.Statut`) et **confirmer
la checklist** (`item_coche.CocheProfesseur`, sans toucher le cochage de l'élève).
SQL visible et paramétré. La notation par critères (`evaluation_activite`) est
différée : le lien critère↔activité n'est pas encore établi dans le modèle.
"""
from __future__ import annotations

from typing import Any

from core.database.db import execute, fetch_all, fetch_one
from core.database.transaction import transaction

# Statuts que le professeur peut poser sur une séance.
STATUTS_SEANCE = ("valide", "en_cours", "bloque", "non_commence")


def get_progression_detail(progression_id: int) -> dict[str, Any] | None:
    """En-tête (élève + parcours) et seances avec preuves, pour évaluer."""
    entete = fetch_one(
        "SELECT pe.Id AS id, pe.Statut AS statut, e.Nom AS nom, e.Prenom AS prenom, "
        "p.Titre AS parcours_titre, p.Identifiant AS parcours_identifiant "
        "FROM progression_parcours pe "
        "JOIN eleve e ON e.Id = pe.eleve_id "
        "JOIN parcours p ON p.Id = pe.parcours_id "
        "WHERE pe.Id = ?",
        (progression_id,),
    )
    if entete is None:
        return None
    entete["seances"] = fetch_all(
        "SELECT pp.Id AS progression_palier_id, pa.Ordre AS ordre, pa.Titre AS titre, pp.Statut AS statut, "
        "(SELECT MAX(Score) FROM tentative_qcm t WHERE t.progression_palier_id = pp.Id) AS meilleur_score, "
        "(SELECT COUNT(*) FROM item_coche ic WHERE ic.progression_palier_id = pp.Id AND ic.CocheEleve = 1) AS coches_eleve, "
        "(SELECT COUNT(*) FROM item_coche ic WHERE ic.progression_palier_id = pp.Id AND ic.CocheProfesseur = 1) AS coches_prof, "
        "(SELECT COUNT(*) FROM depot_eleve d WHERE d.progression_palier_id = pp.Id) AS nb_depots, "
        "(SELECT MIN(Id) FROM checklist c WHERE c.seance_id = pa.Id) AS checklist_id, "
        "(SELECT MIN(Id) FROM activite a WHERE a.seance_id = pa.Id) AS activite_id "
        "FROM progression_palier pp "
        "JOIN seance pa ON pa.Id = pp.seance_id "
        "WHERE pp.progression_parcours_id = ? "
        "ORDER BY pa.Ordre",
        (progression_id,),
    )
    return entete


def set_seance_statut(progression_palier_id: int, statut: str) -> bool:
    """Pose le statut d'une séance (valeur contrôlée). False si le statut est invalide."""
    if statut not in STATUTS_SEANCE:
        return False
    execute(
        "UPDATE progression_palier SET Statut = ? WHERE Id = ?",
        (statut, progression_palier_id),
    )
    return True


def get_checklist_review(progression_palier_id: int) -> dict[str, Any] | None:
    """La checklist d'une séance avec le cochage élève ET prof, pour confirmation."""
    seance = fetch_one(
        "SELECT pp.Id AS id, pp.seance_id AS seance_id, pp.progression_parcours_id AS progression_id, "
        "pa.Titre AS seance_titre "
        "FROM progression_palier pp JOIN seance pa ON pa.Id = pp.seance_id WHERE pp.Id = ?",
        (progression_palier_id,),
    )
    if seance is None:
        return None
    checklist = fetch_one(
        "SELECT Id AS id FROM checklist WHERE seance_id = ? ORDER BY Id LIMIT 1", (seance["seance_id"],)
    )
    if checklist is None:
        return None
    sections = fetch_all(
        "SELECT Id AS id, Titre AS titre FROM section_checklist WHERE checklist_id = ? ORDER BY Id",
        (checklist["id"],),
    )
    for section in sections:
        section["items"] = fetch_all(
            "SELECT i.Id AS id, i.Libelle AS libelle, "
            "COALESCE(ic.CocheEleve, 0) AS coche_eleve, COALESCE(ic.CocheProfesseur, 0) AS coche_prof "
            "FROM item_checklist i "
            "LEFT JOIN item_coche ic ON ic.item_id = i.Id AND ic.progression_palier_id = ? "
            "WHERE i.section_id = ? ORDER BY i.Id",
            (progression_palier_id, section["id"]),
        )
    return {
        "progression_palier_id": progression_palier_id,
        "seance_titre": seance["seance_titre"],
        "progression_id": seance["progression_id"],
        "sections": sections,
    }


def enregistrer_coches_prof(
    progression_palier_id: int, items_coches: set[int]
) -> dict[str, Any] | None:
    """Pose `CocheProfesseur` sur TOUS les items (confirmés → 1, sinon 0), sans
    toucher `CocheEleve`. Upsert sur la clé unique. None si seance/checklist absents."""
    seance = fetch_one(
        "SELECT seance_id AS seance_id FROM progression_palier WHERE Id = ?", (progression_palier_id,)
    )
    if seance is None:
        return None
    checklist = fetch_one(
        "SELECT Id AS id FROM checklist WHERE seance_id = ? ORDER BY Id LIMIT 1", (seance["seance_id"],)
    )
    if checklist is None:
        return None
    items = fetch_all(
        "SELECT i.Id AS id FROM item_checklist i "
        "JOIN section_checklist s ON s.Id = i.section_id WHERE s.checklist_id = ?",
        (checklist["id"],),
    )
    ids = {int(it["id"]) for it in items}
    with transaction() as tx:
        for iid in ids:
            execute(
                "INSERT INTO item_coche "
                "(CocheEleve, CocheProfesseur, item_id, progression_palier_id, CreatedAt, UpdatedAt) "
                "VALUES (0, ?, ?, ?, NOW(), NOW()) "
                "ON DUPLICATE KEY UPDATE CocheProfesseur = VALUES(CocheProfesseur), UpdatedAt = NOW()",
                (1 if iid in items_coches else 0, iid, progression_palier_id),
                tx=tx,
            )
    return {"items": len(ids), "coches": len(ids & items_coches)}
