"""Fixture callable : chaîne pédagogique (starter → parcours → progression → évaluations).

Enchaînement d'entités du Bloc B sans clé naturelle simple : on résout les Id au fil
de l'eau via core.database.db (ADR-078). Dépend du socle (classe, élève, professeur)
et du référentiel (niveau_classe, critères).
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
        "starter_welcome", "version_starter", "parcours", "version_parcours", "palier",
        "affectation_parcours", "progression_eleve", "progression_palier", "activite",
        "evaluation_activite", "evaluation_critere",
    )
    depends_on = ("niveau_classe", "classe", "eleve", "professeur", "critere_observable")

    def load(self) -> None:
        niveau = _id(db.fetch_one("SELECT Id FROM niveau_classe WHERE Code = ?", ("2TNE",)))
        classe = _id(db.fetch_one("SELECT Id FROM classe WHERE Code = ?", ("2TNE-A",)))
        prof = _id(db.fetch_one("SELECT Id FROM professeur WHERE Nom = ?", ("Bernard",)))
        eleve = _id(db.fetch_one("SELECT Id FROM eleve WHERE Identifiant = ?", ("dupont-marie",)))
        crit = [int(r["Id"]) for r in db.fetch_all("SELECT Id FROM critere_observable ORDER BY Id LIMIT 4")]

        sw = db.insert("INSERT INTO starter_welcome (Identifiant, Titre, Presentation, niveau_classe_id, CreatedAt, UpdatedAt) VALUES (?, ?, ?, ?, NOW(), NOW())",
                       ("welcome-reseau", "Welcome Réseau", "Découverte réseau", niveau))
        vs = db.insert("INSERT INTO version_starter (Version, Statut, ActiviteGlissante, OrdreImpose, starter_id, CreatedAt, UpdatedAt) VALUES ('1.0.0','publie',0,1,?,NOW(),NOW())", (sw,))
        parc = db.insert("INSERT INTO parcours (Titre, version_starter_id, CreatedAt, UpdatedAt) VALUES (?, ?, NOW(), NOW())", ("Parcours Welcome Réseau", vs))
        vp = db.insert("INSERT INTO version_parcours (Version, Statut, parcours_id, CreatedAt, UpdatedAt) VALUES ('1.0.0','publie',?,NOW(),NOW())", (parc,))
        pal = db.insert("INSERT INTO palier (Ordre, Titre, Theme, ProductionAttendue, DossierTechniqueFichier, version_parcours_id, CreatedAt, UpdatedAt) VALUES (1,'Palier 1 — Câblage','Réseau','Câble testé','dossier-p1.pdf',?,NOW(),NOW())", (vp,))
        aff = db.insert("INSERT INTO affectation_parcours (DateAffectation, Statut, version_parcours_id, classe_id, professeur_id, CreatedAt, UpdatedAt) VALUES (CURDATE(),'active',?,?,?,NOW(),NOW())", (vp, classe, prof))
        pe = db.insert("INSERT INTO progression_eleve (Statut, DateDebut, eleve_id, affectation_parcours_id, CreatedAt, UpdatedAt) VALUES ('en_cours',CURDATE(),?,?,NOW(),NOW())", (eleve, aff))
        pp = db.insert("INSERT INTO progression_palier (Statut, progression_eleve_id, palier_id, CreatedAt, UpdatedAt) VALUES ('en_cours',?,?,NOW(),NOW())", (pe, pal))
        act = db.insert("INSERT INTO activite (Objectif, palier_id, CreatedAt, UpdatedAt) VALUES ('Câbler et mesurer une liaison',?,NOW(),NOW())", (pal,))
        ea = db.insert("INSERT INTO evaluation_activite (DateEvaluation, Appreciation, progression_palier_id, activite_id, professeur_id, CreatedAt, UpdatedAt) VALUES (NOW(),'Bon travail global',?,?,?,NOW(),NOW())", (pp, act, prof))
        for crit_id, niv in zip(crit, ["atteint", "depasse", "atteint", "partiellement_atteint"]):
            db.execute("INSERT INTO evaluation_critere (Niveau, evaluation_activite_id, critere_id, CreatedAt, UpdatedAt) VALUES (?, ?, ?, NOW(), NOW())", (niv, ea, crit_id))
