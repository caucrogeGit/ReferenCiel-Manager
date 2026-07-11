#!/usr/bin/env python
"""Seed de démonstration — remet la base dans un état de démo complet et cohérent.

But : pouvoir tester **toute** l'application au navigateur avec des comptes connus et
un parcours métier de bout en bout (socle scolaire → référentiel → parcours →
progression → évaluations → bilan).

Réutilise le **code applicatif** (models/services Forge, `import_referentiel`,
`hash_password`) plutôt que du SQL divergent : le seed reste « 100 % Forge ».

Idempotent : réinitialise les tables métier puis reconstruit tout. **Destructif** —
protégé par un dry-run : exécuter avec `--apply` pour écrire réellement.

    .venv/bin/python tools/seed_demo.py            # aperçu (ne touche rien)
    .venv/bin/python tools/seed_demo.py --apply    # applique le seed

Comptes créés (mots de passe de démo) :
    admin@referenciel.local / admin1234   (rôle admin)
    prof@referenciel.local  / prof1234    (rôle professeur, lié à une fiche)
    eleve@referenciel.local / eleve1234   (rôle eleve, lié à une fiche)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))  # exécutable depuis n'importe où (config.py est à la racine)

import config  # noqa: E402, F401  (charge env/* dans os.environ → active core.database.db)
from core.auth.password import hash_password  # noqa: E402
from core.database.db import execute, fetch_all, fetch_one, insert  # noqa: E402

from mvc.models.bilan_eleve_model import creer_bilan  # noqa: E402
from mvc.services.referentiel_importer import import_referentiel  # noqa: E402
_FIXTURE_REFERENTIEL = _ROOT / "docs/specs/json-canonique/examples/json-canonique-ciel-2tne.json"

# Tables métier réinitialisées (l'ordre est indifférent : FK désactivées le temps du reset).
# La table `roles` est PRÉSERVÉE (référentiel de rôles posé par migration).
_TABLES_RESET = [
    "bilan_eleve", "evaluation_critere", "evaluation_activite",
    "item_coche", "item_checklist", "section_checklist", "checklist",
    "reponse_qcm", "tentative_qcm", "choix_qcm", "question_qcm", "qcm",
    "depot_eleve", "activite",
    "progression_palier", "progression_eleve", "affectation_parcours",
    "palier", "version_parcours", "parcours", "version_starter", "starter_welcome",
    "scenario_competence", "scenario_critere", "scenario",
    "activite_competence", "cc_competence", "source", "indicateur_reussite",
    "famille_competence", "connaissance", "critere_observable", "competence",
    "tache", "resultat_attendu", "activite_professionnelle", "pole_activite",
    "referentiel_niveau_classe", "formation",
    "inscription_eleve", "affectation_professeur_classe", "groupe_eleve", "groupe",
    "classe", "niveau_classe", "annee_scolaire",
    "eleve", "professeur",
    "auth_mfa_recovery_codes", "auth_mfa_factors", "auth_tokens", "forge_sessions",
    "user_roles", "users",
]

APPLIQUER = "--apply" in sys.argv


def log(msg: str) -> None:
    print(f"  {msg}")


def reset_tables() -> None:
    # DELETE (DML) plutôt que TRUNCATE (DDL) : le compte applicatif n'a que les droits
    # DML. FK désactivées le temps du reset → l'ordre des tables est indifférent.
    execute("SET FOREIGN_KEY_CHECKS = 0")
    for table in _TABLES_RESET:
        execute(f"DELETE FROM {table}")
    execute("SET FOREIGN_KEY_CHECKS = 1")
    log(f"{len(_TABLES_RESET)} tables métier réinitialisées (roles préservés)")


def role_id(slug: str) -> int:
    row = fetch_one("SELECT id FROM roles WHERE slug = ?", (slug,))
    if row is None:  # roles posés par migration ; recréés si absents
        return insert("INSERT INTO roles (slug, name) VALUES (?, ?)", (slug, slug.capitalize()))
    return int(row["id"])


def creer_compte(email: str, mot_de_passe: str, slug: str) -> int:
    uid = insert(
        "INSERT INTO users (email, password_hash, is_active) VALUES (?, ?, 1)",
        (email, hash_password(mot_de_passe)),
    )
    execute("INSERT INTO user_roles (user_id, role_id) VALUES (?, ?)", (uid, role_id(slug)))
    return uid


def main() -> None:
    if not APPLIQUER:
        print("APERÇU (dry-run) — rien n'est écrit. Relancez avec --apply pour appliquer.\n")
        print("Le seed va :")
        print("  - réinitialiser les tables métier (destructif) ;")
        print("  - importer le référentiel ciel-2tne ;")
        print("  - créer socle (année, classe 2TNE-A, 3 élèves, 1 prof) ;")
        print("  - créer comptes admin/prof/élève (mots de passe de démo) ;")
        print("  - créer parcours + progression + évaluations + bilan.")
        return

    print("Application du seed de démonstration…\n")

    # 1. Reset
    reset_tables()

    # 2. Comptes
    uid_admin = creer_compte("admin@referenciel.local", "admin1234", "admin")
    uid_prof = creer_compte("prof@referenciel.local", "prof1234", "professeur")
    uid_eleve = creer_compte("eleve@referenciel.local", "eleve1234", "eleve")
    log(f"comptes créés : admin(#{uid_admin}), prof(#{uid_prof}), élève(#{uid_eleve})")

    # 3. Référentiel (via le service applicatif) — crée aussi niveau_classe 2TNE + formation
    canonical = json.loads(_FIXTURE_REFERENTIEL.read_text(encoding="utf-8"))
    rapport = import_referentiel(canonical)
    log(f"référentiel importé : {sum(rapport.inseres.values())} objets ({rapport.identifiant})")
    niveau = fetch_one("SELECT Id FROM niveau_classe WHERE Code = ?", ("2TNE",))
    niveau_id = int(niveau["Id"]) if niveau else insert(
        "INSERT INTO niveau_classe (Code, Intitule, CreatedAt, UpdatedAt) "
        "VALUES ('2TNE', 'Seconde TNE', NOW(), NOW())", ()
    )

    # 4. Socle scolaire
    annee_id = insert(
        "INSERT INTO annee_scolaire (Libelle, DateDebut, DateFin, Active, CreatedAt, UpdatedAt) "
        "VALUES ('2025-2026', '2025-09-01', '2026-07-04', 1, NOW(), NOW())", ()
    )
    classe_id = insert(
        "INSERT INTO classe (Code, Libelle, annee_scolaire_id, niveau_classe_id, CreatedAt, UpdatedAt) "
        "VALUES ('2TNE-A', 'Seconde TNE A', ?, ?, NOW(), NOW())", (annee_id, niveau_id)
    )
    prof_id = insert(
        "INSERT INTO professeur (Nom, Prenom, UserId, CreatedAt, UpdatedAt) "
        "VALUES ('Bernard', 'Julie', ?, NOW(), NOW())", (uid_prof,)
    )
    execute(
        "INSERT INTO affectation_professeur_classe "
        "(Role, professeur_id, classe_id, annee_scolaire_id, CreatedAt, UpdatedAt) "
        "VALUES ('Professeur principal', ?, ?, ?, NOW(), NOW())", (prof_id, classe_id, annee_id)
    )
    eleves = [("Dupont", "Marie", "dupont-marie", uid_eleve),
              ("Martin", "Lucas", "martin-lucas", None),
              ("Nguyen", "Emma", "nguyen-emma", None)]
    eleve_ids: list[int] = []
    for nom, prenom, ident, user_id in eleves:
        eid = insert(
            "INSERT INTO eleve (Nom, Prenom, Identifiant, DateNaissance, UserId, CreatedAt, UpdatedAt) "
            "VALUES (?, ?, ?, '2009-05-15', ?, NOW(), NOW())", (nom, prenom, ident, user_id)
        )
        eleve_ids.append(eid)
        execute(
            "INSERT INTO inscription_eleve "
            "(DateInscription, eleve_id, classe_id, annee_scolaire_id, CreatedAt, UpdatedAt) "
            "VALUES (CURDATE(), ?, ?, ?, NOW(), NOW())", (eid, classe_id, annee_id)
        )
    log(f"socle : classe 2TNE-A, prof Bernard, {len(eleve_ids)} élèves inscrits")

    # 5. Bloc B — parcours → progression → évaluations (pour l'élève lié, Dupont Marie)
    sw_id = insert(
        "INSERT INTO starter_welcome (Identifiant, Titre, Presentation, niveau_classe_id, CreatedAt, UpdatedAt) "
        "VALUES ('welcome-reseau', 'Welcome Réseau', 'Découverte réseau', ?, NOW(), NOW())", (niveau_id,)
    )
    vs_id = insert(
        "INSERT INTO version_starter (Version, Statut, ActiviteGlissante, OrdreImpose, starter_id, CreatedAt, UpdatedAt) "
        "VALUES ('1.0.0', 'publie', 0, 1, ?, NOW(), NOW())", (sw_id,)
    )
    parc_id = insert(
        "INSERT INTO parcours (Titre, version_starter_id, CreatedAt, UpdatedAt) "
        "VALUES ('Parcours Welcome Réseau', ?, NOW(), NOW())", (vs_id,)
    )
    vp_id = insert(
        "INSERT INTO version_parcours (Version, Statut, parcours_id, CreatedAt, UpdatedAt) "
        "VALUES ('1.0.0', 'publie', ?, NOW(), NOW())", (parc_id,)
    )
    pal_id = insert(
        "INSERT INTO palier (Ordre, Titre, Theme, ProductionAttendue, DossierTechniqueFichier, version_parcours_id, CreatedAt, UpdatedAt) "
        "VALUES (1, 'Palier 1 — Câblage', 'Réseau', 'Câble testé', 'dossier-p1.pdf', ?, NOW(), NOW())", (vp_id,)
    )
    aff_id = insert(
        "INSERT INTO affectation_parcours (DateAffectation, Statut, version_parcours_id, classe_id, professeur_id, CreatedAt, UpdatedAt) "
        "VALUES (CURDATE(), 'active', ?, ?, ?, NOW(), NOW())", (vp_id, classe_id, prof_id)
    )
    act_id = insert(
        "INSERT INTO activite (Objectif, palier_id, CreatedAt, UpdatedAt) "
        "VALUES ('Câbler et mesurer une liaison', ?, NOW(), NOW())", (pal_id,)
    )
    # Progression pour chaque élève ; évaluations complètes pour le 1er (compte lié).
    crit_ids = [int(r["Id"]) for r in fetch_all("SELECT Id FROM critere_observable ORDER BY Id LIMIT 4")]
    for i, eid in enumerate(eleve_ids):
        pe_id = insert(
            "INSERT INTO progression_eleve (Statut, DateDebut, eleve_id, affectation_parcours_id, CreatedAt, UpdatedAt) "
            "VALUES ('en_cours', CURDATE(), ?, ?, NOW(), NOW())", (eid, aff_id)
        )
        pp_id = insert(
            "INSERT INTO progression_palier (Statut, progression_eleve_id, palier_id, CreatedAt, UpdatedAt) "
            "VALUES ('en_cours', ?, ?, NOW(), NOW())", (pe_id, pal_id)
        )
        if i == 0 and crit_ids:  # évaluations + bilan pour l'élève relié à un compte
            ea_id = insert(
                "INSERT INTO evaluation_activite (DateEvaluation, Appreciation, progression_palier_id, activite_id, professeur_id, CreatedAt, UpdatedAt) "
                "VALUES (NOW(), 'Bon travail global', ?, ?, ?, NOW(), NOW())", (pp_id, act_id, prof_id)
            )
            niveaux = ["atteint", "depasse", "atteint", "partiellement_atteint"]
            for crit_id, niv in zip(crit_ids, niveaux):
                execute(
                    "INSERT INTO evaluation_critere (Niveau, evaluation_activite_id, critere_id, CreatedAt, UpdatedAt) "
                    "VALUES (?, ?, ?, NOW(), NOW())", (niv, ea_id, crit_id)
                )
            bilan_id = creer_bilan(
                progression_eleve_id=pe_id, professeur_id=prof_id,
                appreciation="Élève sérieux, bonne progression sur le câblage.", statut="publie",
            )
            log(f"évaluations ({len(crit_ids)} critères) + bilan #{bilan_id} pour Dupont Marie")
    log("Bloc B : parcours Welcome Réseau affecté, 3 progressions")

    print("\n✓ Seed appliqué. Comptes de démonstration :")
    print("    admin@referenciel.local / admin1234")
    print("    prof@referenciel.local  / prof1234   (→ /mes-classes, /suivi, /bilan)")
    print("    eleve@referenciel.local / eleve1234  (→ /mon-parcours)")


if __name__ == "__main__":
    main()
