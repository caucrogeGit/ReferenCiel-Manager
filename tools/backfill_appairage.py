#!/usr/bin/env python
"""Backfill de l'appairage 1-1 Scénario ↔ Séquence (ADR-029).

Crée la séquence jumelle manquante des scénarios existants (titre partagé,
niveau vide, statut brouillon) et le lien scenario_sequence. Additif et
réversible : aucune donnée n'est supprimée.

Convention Forge du projet (charte §7) : **affichage par défaut ; `--run`
exécute réellement.**

Usage :
    .venv/bin/python tools/backfill_appairage.py            # montre le plan
    .venv/bin/python tools/backfill_appairage.py --run      # crée les jumelles

Réversible : pour annuler, supprimer les séquences créées (et leurs liens).
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
os.chdir(_ROOT)
sys.path.insert(0, str(_ROOT))

import config  # noqa: F401,E402  — amorce env/dev → os.environ
from mvc.models.scenario_editeur_model import (  # noqa: E402
    lister_scenarios_sans_sequence,
    creer_sequence_jumelle,
)


def main() -> int:
    run = "--run" in sys.argv[1:]
    orphelins = lister_scenarios_sans_sequence()

    if not orphelins:
        print("Aucun scénario orphelin : tous ont déjà une séquence appairée.")
        return 0

    print(f"{len(orphelins)} scénario(s) sans séquence appairée :")
    for sc in orphelins:
        print(f"  - scénario {sc['Id']} « {sc['Titre']} »")

    if not run:
        print("\n(plan seulement — relancer avec --run pour créer les séquences jumelles)")
        return 0

    print()
    for sc in orphelins:
        sequence_id = creer_sequence_jumelle(int(sc["Id"]), str(sc["Titre"]))
        print(f"  ✓ scénario {sc['Id']} → séquence {sequence_id} créée et liée")
    print(f"\n{len(orphelins)} séquence(s) jumelle(s) créée(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
