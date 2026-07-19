#!/usr/bin/env python
"""Remet la base à un état vierge, puis recrée les comptes de démarrage.

Outil de développement : efface toutes les données applicatives pour repartir
d'une base propre, en préservant ce qui est structurel (rôles RBAC semés par
migration, journal des migrations). Option pour conserver le référentiel importé.

Convention Forge du projet (charte §7, comme `fixtures:load/purge`) :
**affichage par défaut ; `--run` exécute réellement.**

Usage :
    .venv/bin/python tools/reset_vierge.py                     # montre le plan
    .venv/bin/python tools/reset_vierge.py --run               # efface tout + comptes
    .venv/bin/python tools/reset_vierge.py --run --garder-referentiel
    .venv/bin/python tools/reset_vierge.py --run --sans-comptes

Notes :
- `TRUNCATE` (remet l'AUTO_INCREMENT à 1) exige le privilège DROP : la purge passe
  par la connexion d'ADMINISTRATION (le compte applicatif est DML seul, ADR-054).
- Les comptes de démarrage ont des mots de passe volontairement courts, sous la
  politique (min. 8 car., ADR-014). Ils fonctionnent au login (hachage direct,
  hors validation) mais seraient refusés via l'UI. À usage de DÉMO/DEV uniquement.
- Une sauvegarde préalable est recommandée : `mysqldump ... > backup.sql`.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

# Le script s'exécute depuis la racine du projet : les chemins relatifs (env/) et
# l'import de la config en dépendent.
_ROOT = Path(__file__).resolve().parent.parent
os.chdir(_ROOT)
sys.path.insert(0, str(_ROOT))

import config  # noqa: F401,E402  — amorce env/dev → os.environ (ADR-060)
from core.auth.password import hash_password  # noqa: E402
from core.database import db  # noqa: E402
from core.database.connection import get_backend  # noqa: E402
from core.database.transaction import transaction  # noqa: E402

# Tables structurelles : jamais effacées (sinon l'app casse).
#  - roles : semé par les migrations RBAC (slugs admin/professeur/eleve) ;
#  - forge_migrations : journal des migrations appliquées.
KEEP_STRUCTUREL = frozenset({"roles", "forge_migrations"})

# Tables de CONTENU d'un référentiel (miroir exact de ce que l'importeur écrit,
# mvc/services/referentiel_importer.py). Préservées avec --garder-referentiel.
KEEP_REFERENTIEL = frozenset({
    "formation",
    "referentiel_niveau_classe",
    "source",
    "pole_activite",
    "activite_professionnelle",
    "tache",
    "resultat_attendu",
    "competence",
    "connaissance",
    "critere_observable",
    "indicateur_reussite",
    "famille_competence",
    "activite_competence",
    "cc_competence",
})

# Comptes de démarrage recréés après la purge (email, mot de passe, slug de rôle).
# DÉMO/DEV : mots de passe courts assumés (voir docstring).
COMPTES = (
    ("admin@referenciel-manager.com", "admin", "admin"),
    ("prof@referenciel-manager.com", "prof", "professeur"),
    ("eleve@referenciel-manager.com", "eleve", "eleve"),
)


def _toutes_les_tables() -> list[str]:
    return [
        next(iter(r.values()))
        for r in db.fetch_all(
            "SELECT TABLE_NAME FROM information_schema.tables "
            "WHERE TABLE_SCHEMA = DATABASE()"
        )
    ]


def _purger(tables: list[str]) -> None:
    """Vide les tables via la connexion d'administration (TRUNCATE = privilège DROP)."""
    admin = get_backend().get_admin_connection(database=os.environ["DB_NAME"])
    try:
        cur = admin.cursor()
        cur.execute("SET FOREIGN_KEY_CHECKS = 0")
        for t in tables:
            cur.execute(f"TRUNCATE TABLE `{t}`")
        cur.execute("SET FOREIGN_KEY_CHECKS = 1")
        admin.commit()
        cur.close()
    finally:
        admin.close()


def _creer_comptes() -> None:
    """Recrée les comptes de démarrage (mot de passe haché, rôle par slug)."""
    with transaction() as tx:
        for email, mdp, slug in COMPTES:
            role = db.fetch_one("SELECT id FROM roles WHERE slug = ?", (slug,), tx=tx)
            if role is None:
                raise SystemExit(f"rôle introuvable : {slug!r} — abandon (rien n'est validé)")
            uid = db.insert(
                "INSERT INTO users (email, password_hash, is_active) VALUES (?, ?, 1)",
                (email, hash_password(mdp)), tx=tx,
            )
            db.execute("INSERT INTO user_roles (user_id, role_id) VALUES (?, ?)",
                       (uid, role["id"]), tx=tx)
            print(f"  + {email}  (uid={uid}, rôle={slug})")


def main(argv: list[str]) -> int:
    run = "--run" in argv
    garder_ref = "--garder-referentiel" in argv
    sans_comptes = "--sans-comptes" in argv

    keep = set(KEEP_STRUCTUREL)
    if garder_ref:
        keep |= KEEP_REFERENTIEL

    tables = _toutes_les_tables()
    a_vider = sorted(t for t in tables if t not in keep)

    # Plan (toujours affiché).
    print(f"Base : {os.environ.get('DB_NAME', '?')}  ({len(tables)} tables)")
    print(f"Conservées ({len(keep & set(tables))}) : {', '.join(sorted(keep & set(tables)))}")
    print(f"À vider ({len(a_vider)}) : {', '.join(a_vider)}")
    if garder_ref:
        print("Option : --garder-referentiel (le référentiel importé est préservé).")
    print("Comptes recréés :" if not sans_comptes else "Comptes : AUCUN (--sans-comptes).")
    if not sans_comptes:
        for email, _, slug in COMPTES:
            print(f"    {email}  (rôle {slug})")

    if not run:
        print("\n(affichage seul — relancez avec --run pour exécuter)")
        return 0

    print("\n[RUN] purge en cours…")
    _purger(a_vider)
    print(f"  {len(a_vider)} table(s) vidée(s).")
    if not sans_comptes:
        _creer_comptes()
    print("Terminé.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
