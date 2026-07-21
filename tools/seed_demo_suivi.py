#!/usr/bin/env python
"""Jeu de démo pour le suivi/évaluation (ADR-033) — DÉV uniquement.

Sème un ensemble cohérent et testable : structure scolaire, une classe liée au
compte `prof`, des élèves, une séquence (appairée à un scénario du référentiel
2tne-ciel) avec des séances qui observent des compétences/critères, et des
progressions élève variées (dont « en attente de validation »).

Convention Forge du projet : **affichage par défaut ; `--run` exécute**.

Usage :
    .venv/bin/python tools/seed_demo_suivi.py            # montre le plan
    .venv/bin/python tools/seed_demo_suivi.py --run      # sème

Idempotent-léger : si la classe « DEMO-2TNE » existe déjà, ne fait rien.
"""
from __future__ import annotations

import os
import sys
from datetime import datetime, timezone
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
os.chdir(_ROOT)
sys.path.insert(0, str(_ROOT))

import config  # noqa: F401,E402
from core.database.db import fetch_all, fetch_one, execute, insert  # noqa: E402
from mvc.models.scenario_editeur_model import creer_scenario  # noqa: E402

_PROF_USER_ID = 2          # prof@referenciel-manager.com
_FORMATION_ID = 1          # 2TNE
_REFERENTIEL_ID = 1        # 2tne-ciel
_CLASSE_CODE = "DEMO-2TNE"

_ELEVES = [("Dupont", "Marie"), ("Martin", "Léa"), ("Bernard", "Hugo")]
# Statut par (élève, séance) — de quoi peupler la file « à évaluer ».
_STATUTS = [
    ["en_attente_validation", "en_cours"],       # Marie
    ["en_cours", "a_reprendre"],                 # Léa
    ["validee", "non_commencee"],                # Hugo
]


def _now() -> datetime:
    return datetime.now(timezone.utc)


def seed() -> None:
    now = _now()
    # Structure scolaire.
    nc = insert("INSERT INTO niveau_classe (Code, Intitule, CreatedAt, UpdatedAt) VALUES (?, ?, ?, ?)",
                ("SECONDE_PRO", "Seconde professionnelle", now, now))
    fn = insert("INSERT INTO formation_niveau (Code, Libelle, OrdreIndicatif, formation_id, niveau_classe_id, CreatedAt, UpdatedAt) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                ("2TNE-2NDE", "2TNE — Seconde", 1, _FORMATION_ID, nc, now, now))
    annee = insert("INSERT INTO annee_scolaire (Libelle, CreatedAt, UpdatedAt) VALUES (?, ?, ?)",
                   ("2025-2026", now, now))
    classe = insert("INSERT INTO classe (Code, Libelle, annee_scolaire_id, formation_niveau_id, CreatedAt, UpdatedAt) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    (_CLASSE_CODE, "Démo 2TNE A", annee, fn, now, now))

    # Professeur lié au compte prof (créé si absent).
    prof = fetch_one("SELECT Id FROM professeur WHERE UserId = ?", (_PROF_USER_ID,))
    prof_id = prof["Id"] if prof else insert(
        "INSERT INTO professeur (Nom, Prenom, UserId, CreatedAt, UpdatedAt) VALUES (?, ?, ?, ?, ?)",
        ("Démo", "Professeur", _PROF_USER_ID, now, now))
    execute("INSERT INTO classe_professeur (classe_id, professeur_id) VALUES (?, ?)", (classe, prof_id))

    # Élèves.
    eleve_ids = [
        insert("INSERT INTO eleve (Nom, Prenom, classe_id, CreatedAt, UpdatedAt) VALUES (?, ?, ?, ?, ?)",
               (nom, prenom, classe, now, now))
        for nom, prenom in _ELEVES
    ]

    # Séquence + scénario appairés (référentiel 2tne-ciel).
    scid = creer_scenario("Démo — Installer une liaison Ethernet", _REFERENTIEL_ID)
    sqid = fetch_one("SELECT sequence_id FROM scenario_sequence WHERE scenario_id = ?", (scid,))["sequence_id"]

    # Deux compétences (avec critères) du référentiel → liées au scénario, puis
    # observées par deux séances.
    comps = fetch_all(
        "SELECT DISTINCT cp.Id AS comp, cp.Code AS code, cp.Intitule AS intitule "
        "FROM competence cp JOIN critere_observable c ON c.competence_id = cp.Id "
        "WHERE cp.referentiel_id = ? ORDER BY cp.Code LIMIT 2", (_REFERENTIEL_ID,))
    seance_ids: list[int] = []
    for i, comp in enumerate(comps, start=1):
        criteres = fetch_all("SELECT Id FROM critere_observable WHERE competence_id = ? ORDER BY Id LIMIT 3", (comp["comp"],))
        for cr in criteres:
            execute("INSERT INTO scenario_critere (scenario_id, critere_observable_id) VALUES (?, ?)", (scid, cr["Id"]))
        seaid = insert("INSERT INTO seance (Ordre, Titre, sequence_id, CreatedAt, UpdatedAt) VALUES (?, ?, ?, ?, ?)",
                       (i, f"Séance {i} — {comp['intitule'][:40]}", sqid, now, now))
        execute("INSERT INTO seance_competence (seance_id, competence_id, Role, CreatedAt, UpdatedAt) VALUES (?, ?, ?, ?, ?)",
                (seaid, comp["comp"], "evaluee", now, now))
        for cr in criteres:
            execute("INSERT INTO seance_critere (seance_id, critere_observable_id, CreatedAt, UpdatedAt) VALUES (?, ?, ?, ?)",
                    (seaid, cr["Id"], now, now))
        seance_ids.append(seaid)

    # Progressions élève (une par élève sur la séquence, puis par séance).
    for idx, eleve_id in enumerate(eleve_ids):
        psq = insert("INSERT INTO progression_sequence (Statut, DateDebut, eleve_id, sequence_id, CreatedAt, UpdatedAt) "
                     "VALUES (?, ?, ?, ?, ?, ?)", ("en_cours", now, eleve_id, sqid, now, now))
        for seaid, statut in zip(seance_ids, _STATUTS[idx]):
            execute("INSERT INTO progression_seance (Statut, progression_sequence_id, seance_id, CreatedAt, UpdatedAt) "
                    "VALUES (?, ?, ?, ?, ?)", (statut, psq, seaid, now, now))

    print(f"  Classe {classe}, {len(eleve_ids)} élèves, séquence {sqid}, {len(seance_ids)} séances, progressions semées.")


def main() -> int:
    if fetch_one("SELECT Id FROM classe WHERE Code = ?", (_CLASSE_CODE,)) is not None:
        print(f"Le jeu de démo existe déjà (classe {_CLASSE_CODE}). Rien à faire.")
        return 0
    if "--run" not in sys.argv[1:]:
        print("Plan : structure scolaire + classe DEMO-2TNE (liée au prof) + 3 élèves + "
              "1 séquence (référentiel 2tne-ciel) avec 2 séances observant des compétences/"
              "critères + progressions variées (dont « en attente de validation »).")
        print("\n(relancer avec --run pour semer)")
        return 0
    seed()
    print("Jeu de démo semé.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
