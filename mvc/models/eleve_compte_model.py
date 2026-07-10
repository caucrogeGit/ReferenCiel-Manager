# pyright: strict
"""Gestion des comptes élèves par l'admin (socle).

Crée un compte `users`, lui pose le rôle `eleve` et le **lie** à une fiche `Eleve`
(`eleve.UserId`) — en une seule transaction. SQL visible et paramétré, hash de mot
de passe délégué au cœur Forge (`core.auth.password.hash_password`). Lecture : état
des comptes par élève, et liste des élèves sans compte (pour le formulaire).
"""
from __future__ import annotations

import re
from typing import Any

from core.auth.password import hash_password
from core.database.db import execute, fetch_all, fetch_one, insert
from core.database.transaction import transaction

# Validation d'email volontairement simple (le cœur ne valide pas le format, seulement
# la présence). On refuse un identifiant nu comme `admin` : il faut `utilisateur@domaine`.
_EMAIL_RE = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")


def email_est_valide(email: str) -> bool:
    return bool(_EMAIL_RE.fullmatch(email.strip()))


def email_existe(email: str) -> bool:
    return fetch_one("SELECT id FROM users WHERE email = ?", (email,)) is not None


def list_eleves_avec_compte() -> list[dict[str, Any]]:
    """Tous les élèves avec l'email de leur compte lié (ou NULL si aucun)."""
    return fetch_all(
        "SELECT e.Id AS id, e.Nom AS nom, e.Prenom AS prenom, u.email AS email "
        "FROM eleve e LEFT JOIN users u ON u.id = e.UserId "
        "ORDER BY e.Nom, e.Prenom"
    )


def eleves_sans_compte() -> list[dict[str, Any]]:
    """Élèves non encore rattachés à un compte (candidats du formulaire)."""
    return fetch_all(
        "SELECT Id AS id, Nom AS nom, Prenom AS prenom FROM eleve "
        "WHERE UserId IS NULL ORDER BY Nom, Prenom"
    )


def creer_compte_eleve(eleve_id: int, email: str, password: str) -> int:
    """Crée le compte, pose le rôle `eleve` et le lie à la fiche — transactionnel.

    Retourne l'id du compte créé. Suppose les invariants vérifiés en amont (email
    valide et libre, mot de passe présent, élève sans compte). Le lien n'écrase
    jamais un rattachement existant (`WHERE UserId IS NULL`).
    """
    password_hash = hash_password(password)
    with transaction() as tx:
        user_id = insert(
            "INSERT INTO users (email, password_hash, is_active) VALUES (?, ?, ?)",
            (email, password_hash, 1),
            tx=tx,
        )
        execute(
            "INSERT INTO user_roles (user_id, role_id) SELECT ?, id FROM roles WHERE slug = ?",
            (user_id, "eleve"),
            tx=tx,
        )
        execute(
            "UPDATE eleve SET UserId = ? WHERE Id = ? AND UserId IS NULL",
            (user_id, eleve_id),
            tx=tx,
        )
    return user_id
