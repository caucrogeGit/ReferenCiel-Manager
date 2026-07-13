#!/usr/bin/env python
"""Charge en base les référentiels canoniques livrés (`data/referentiels/*.json`).

Étape de mise en service (ADR-016) : les référentiels vivent versionnés dans le
projet et sont chargés en base une fois l'application installée par l'établissement.
Chaque JSON est **validé** contre le schéma (`canonical_validator`) puis **importé**
(`referentiel_importer`, upsert best-effort). **Idempotent** : réimporter un même
`identifiant` remplace son contenu.

Usage :
    .venv/bin/python tools/charger_referentiels.py            # valide + importe
    .venv/bin/python tools/charger_referentiels.py --check    # valide seulement
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

# Le script s'exécute depuis la racine du projet : les chemins relatifs (env/,
# data/, schemas/) et l'import de la config en dépendent.
_ROOT = Path(__file__).resolve().parent.parent
os.chdir(_ROOT)
sys.path.insert(0, str(_ROOT))

import config  # noqa: F401,E402  — amorce env/dev → os.environ (ADR-060)
from mvc.services.canonical_validator import validate_referentiel_canonical  # noqa: E402
from mvc.services.referentiel_importer import import_referentiel  # noqa: E402

_DIR = Path("data/referentiels")


def main(argv: list[str]) -> int:
    check_only = "--check" in argv
    fichiers = sorted(_DIR.glob("*.json"))
    if not fichiers:
        print(f"Aucun référentiel dans {_DIR}/ (rien à charger).")
        return 0

    erreurs_totales = 0
    for path in fichiers:
        print(f"\n=== {path.name} ===")
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            print(f"  [ERREUR] lecture/JSON : {exc}", file=sys.stderr)
            erreurs_totales += 1
            continue

        erreurs_schema = validate_referentiel_canonical(data)
        if erreurs_schema:
            print(f"  [INVALIDE] {len(erreurs_schema)} erreur(s) de schéma :", file=sys.stderr)
            for e in erreurs_schema:
                print(f"    - {e}", file=sys.stderr)
            erreurs_totales += 1
            continue
        print("  [OK] conforme au schéma")

        if check_only:
            continue

        rapport = import_referentiel(data)
        total_inseres = sum(rapport.inseres.values())
        mode = "remplacé" if rapport.remplacement else "créé"
        print(f"  [IMPORT] {rapport.identifiant} {mode} — {total_inseres} objet(s)")
        if not rapport.ok:
            print(f"  [ERREURS IMPORT] {len(rapport.erreurs)} :", file=sys.stderr)
            for e in rapport.erreurs:
                print(f"    - {e}", file=sys.stderr)
            erreurs_totales += 1

    print()
    if erreurs_totales:
        print(f"Terminé avec {erreurs_totales} référentiel(s) en erreur.", file=sys.stderr)
        return 1
    action = "validé(s)" if check_only else "chargé(s)"
    print(f"OK — {len(fichiers)} référentiel(s) {action}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
