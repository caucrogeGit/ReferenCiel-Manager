"""Déroulé ordonné d'une séance : les ElementSeance (ADR-032, phase B).

Éléments génériques (type, titre, contenu libre, durée, obligatoire, rôle
pédagogique). Les colonnes qcm_id/checklist_id existent pour une future
référence polymorphe, mais ne sont pas encore pilotées par l'UI.
"""

from datetime import datetime, timezone

from core.database.db import fetch_all, fetch_one, execute, insert

# Types d'élément (exemple CIEL). L'ordre reflète un déroulé typique.
TYPES = (
    "consigne", "video", "document", "outil_interactif", "qcm",
    "travail_pratique", "depot", "checklist", "validation_prof", "synthese",
)
TYPE_LABELS = {
    "consigne": "Consigne / présentation",
    "video": "Vidéo",
    "document": "Document",
    "outil_interactif": "Outil interactif",
    "qcm": "QCM",
    "travail_pratique": "Travail pratique",
    "depot": "Dépôt élève",
    "checklist": "Checklist",
    "validation_prof": "Validation professeur",
    "synthese": "Synthèse",
}


def get_elements(seance_id):
    """Éléments d'une séance, dans l'ordre."""
    return fetch_all(
        "SELECT * FROM element_seance WHERE seance_id = ? ORDER BY Ordre, Id", (seance_id,)
    )


def get_element(element_id):
    return fetch_one("SELECT * FROM element_seance WHERE Id = ?", (element_id,))


def ajouter(seance_id, type_, titre, contenu, duree, obligatoire, role):
    """Ajoute un élément en fin de déroulé (ordre = max + 1)."""
    row = fetch_one("SELECT COALESCE(MAX(Ordre), 0) AS m FROM element_seance WHERE seance_id = ?", (seance_id,))
    ordre = int(row["m"]) + 1 if row else 1
    now = datetime.now(timezone.utc)
    return insert(
        "INSERT INTO element_seance (Ordre, Type, Titre, Contenu, DureeMinutes, Obligatoire, "
        "RolePedagogique, seance_id, CreatedAt, UpdatedAt) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (ordre, type_, titre, contenu, duree, 1 if obligatoire else 0, role, seance_id, now, now),
    )


def maj(element_id, titre, contenu, duree, obligatoire, role):
    """Met à jour un élément (pas son type ni son ordre)."""
    execute(
        "UPDATE element_seance SET Titre = ?, Contenu = ?, DureeMinutes = ?, Obligatoire = ?, "
        "RolePedagogique = ?, UpdatedAt = ? WHERE Id = ?",
        (titre, contenu, duree, 1 if obligatoire else 0, role, datetime.now(timezone.utc), element_id),
    )


def supprimer(element_id):
    execute("DELETE FROM element_seance WHERE Id = ?", (element_id,))


def deplacer(element_id, sens):
    """Échange l'ordre avec l'élément voisin (sens : 'haut' ou 'bas')."""
    el = get_element(element_id)
    if el is None:
        return
    seance_id, ordre = el["seance_id"], el["Ordre"]
    if sens == "haut":
        voisin = fetch_one(
            "SELECT Id, Ordre FROM element_seance WHERE seance_id = ? AND Ordre < ? "
            "ORDER BY Ordre DESC LIMIT 1", (seance_id, ordre),
        )
    else:
        voisin = fetch_one(
            "SELECT Id, Ordre FROM element_seance WHERE seance_id = ? AND Ordre > ? "
            "ORDER BY Ordre ASC LIMIT 1", (seance_id, ordre),
        )
    if voisin is None:
        return
    now = datetime.now(timezone.utc)
    execute("UPDATE element_seance SET Ordre = ?, UpdatedAt = ? WHERE Id = ?", (voisin["Ordre"], now, element_id))
    execute("UPDATE element_seance SET Ordre = ?, UpdatedAt = ? WHERE Id = ?", (ordre, now, voisin["Id"]))
