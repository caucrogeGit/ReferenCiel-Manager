"""Fixture callable : chaîne pédagogique (parcours → palier → dossier → progression → évaluations).

Modèle canonique aplati (ADR-022) : le Parcours est l'objet racine (rattaché au
NiveauClasse), il contient des Paliers ; chaque palier porte un DossierTechnique
(ressources + QCM de validation). L'élève a une ProgressionParcours (directe, sans
affectation) déclinée en ProgressionPalier. On résout les Id au fil de l'eau via
core.database.db (ADR-078). Dépend du socle (classe, élève, professeur) et du
référentiel (niveau_classe, critères).
"""
from typing import Any
from forge_mvc_fixtures import Fixture
from core.database import db


def _id(row: "dict[str, Any] | None") -> int:
    if row is None:
        raise RuntimeError("Fixture bloc_b : dépendance introuvable (socle/référentiel non chargé ?).")
    return int(row["Id"])


class BlocBFixture(Fixture):
    tables = (
        "parcours", "palier", "dossier_technique", "ressource_dossier", "qcm",
        "classe_professeur", "professeur_parcours",
        "progression_parcours", "progression_palier", "activite",
        "evaluation_activite", "evaluation_critere",
    )
    depends_on = ("niveau_classe", "classe", "eleve", "professeur", "critere_observable")

    def load(self) -> None:
        niveau = _id(db.fetch_one("SELECT Id FROM niveau_classe WHERE Code = ?", ("2TNE",)))
        classe = _id(db.fetch_one("SELECT Id FROM classe WHERE Code = ?", ("2TNE-A",)))
        prof = _id(db.fetch_one("SELECT Id FROM professeur WHERE Nom = ?", ("Bernard",)))
        eleve = _id(db.fetch_one("SELECT Id FROM eleve WHERE Identifiant = ?", ("dupont-marie",)))
        crit = [int(r["Id"]) for r in db.fetch_all("SELECT Id FROM critere_observable ORDER BY Id LIMIT 4")]

        # Parcours canonique (rattaché au niveau de classe) et ses liens n-n.
        parc = db.insert(
            "INSERT INTO parcours (Identifiant, Titre, Presentation, Statut, ActiviteGlissante, OrdreImpose, niveau_classe_id, CreatedAt, UpdatedAt) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, NOW(), NOW())",
            ("welcome-reseau", "Parcours Welcome Réseau", "Découverte du réseau et du câblage.", "publie", 0, 1, niveau),
        )
        db.execute("INSERT INTO professeur_parcours (professeur_id, parcours_id) VALUES (?, ?)", (prof, parc))
        db.execute("INSERT INTO classe_professeur (classe_id, professeur_id) VALUES (?, ?)", (classe, prof))

        # Palier -> dossier technique (ressource markdown + QCM de validation).
        pal = db.insert(
            "INSERT INTO seance (Ordre, Titre, Theme, ProductionAttendue, parcours_id, CreatedAt, UpdatedAt) "
            "VALUES (1, 'Palier 1 — Câblage', 'Réseau', 'Câble testé et validé', ?, NOW(), NOW())",
            (parc,),
        )
        dt = db.insert(
            "INSERT INTO dossier_technique (Titre, seance_id, CreatedAt, UpdatedAt) VALUES (?, ?, NOW(), NOW())",
            ("Dossier technique — Câblage", pal),
        )
        db.execute(
            "INSERT INTO ressource_dossier (Type, Titre, Ordre, Contenu, dossier_technique_id, CreatedAt, UpdatedAt) "
            "VALUES ('markdown', 'Consignes de câblage', 1, ?, ?, NOW(), NOW())",
            ("# Câblage RJ45\n\nRespecter la norme **T568B** et tester la continuité.", dt),
        )
        db.insert(
            "INSERT INTO qcm (FormatReponse, SeuilValidation, dossier_technique_id, CreatedAt, UpdatedAt) "
            "VALUES ('qcm', '70', ?, NOW(), NOW())",
            (dt,),
        )

        # Progression directe de l'élève sur le parcours, déclinée par palier.
        pe = db.insert(
            "INSERT INTO progression_parcours (Statut, DateDebut, eleve_id, parcours_id, CreatedAt, UpdatedAt) "
            "VALUES ('en_cours', CURDATE(), ?, ?, NOW(), NOW())",
            (eleve, parc),
        )
        pp = db.insert(
            "INSERT INTO progression_palier (Statut, progression_parcours_id, seance_id, CreatedAt, UpdatedAt) "
            "VALUES ('en_cours', ?, ?, NOW(), NOW())",
            (pe, pal),
        )
        act = db.insert(
            "INSERT INTO activite (Objectif, seance_id, CreatedAt, UpdatedAt) VALUES ('Câbler et mesurer une liaison', ?, NOW(), NOW())",
            (pal,),
        )
        ea = db.insert(
            "INSERT INTO evaluation_activite (DateEvaluation, Appreciation, progression_palier_id, activite_id, professeur_id, CreatedAt, UpdatedAt) "
            "VALUES (NOW(), 'Bon travail global', ?, ?, ?, NOW(), NOW())",
            (pp, act, prof),
        )
        for crit_id, niv in zip(crit, ["atteint", "depasse", "atteint", "partiellement_atteint"]):
            db.execute(
                "INSERT INTO evaluation_critere (Niveau, evaluation_activite_id, critere_id, CreatedAt, UpdatedAt) VALUES (?, ?, ?, NOW(), NOW())",
                (niv, ea, crit_id),
            )
