# pyright: strict
"""Gestion des comptes professeurs par l'admin (socle) — symétrique de eleve.

Crée un compte `users`, lui pose le rôle `professeur` et le **lie** à une fiche
`Professeur` (`professeur.UserId`), en une transaction. Hash du mot de passe
délégué au cœur Forge. Une fois lié, l'évaluation peut être attribuée au
professeur connecté (cf. `notation_critere_model`).
"""
from __future__ import annotations

import re
from typing import Any

from core.auth.password import hash_password
from core.database.db import execute, fetch_all, fetch_one, insert
from core.database.transaction import transaction

_EMAIL_RE = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")


def email_est_valide(email: str) -> bool:
    return bool(_EMAIL_RE.fullmatch(email.strip()))


def email_existe(email: str) -> bool:
    return fetch_one("SELECT id FROM users WHERE email = ?", (email,)) is not None


def list_professeurs_avec_compte() -> list[dict[str, Any]]:
    """Tous les professeurs avec l'email de leur compte lié (ou NULL)."""
    return fetch_all(
        "SELECT p.Id AS id, p.Nom AS nom, p.Prenom AS prenom, u.email AS email "
        "FROM professeur p LEFT JOIN users u ON u.id = p.UserId "
        "ORDER BY p.Nom, p.Prenom"
    )


def professeurs_sans_compte() -> list[dict[str, Any]]:
    """Professeurs non encore rattachés à un compte (candidats du formulaire)."""
    return fetch_all(
        "SELECT Id AS id, Nom AS nom, Prenom AS prenom FROM professeur "
        "WHERE UserId IS NULL ORDER BY Nom, Prenom"
    )


def creer_compte_professeur(professeur_id: int, email: str, password: str) -> int:
    """Crée le compte, pose le rôle `professeur` et le lie à la fiche — transactionnel.

    Retourne l'id du compte. Suppose les invariants vérifiés (email valide et libre,
    mot de passe présent, professeur sans compte). Le lien n'écrase jamais un
    rattachement existant (`WHERE UserId IS NULL`).
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
            (user_id, "professeur"),
            tx=tx,
        )
        execute(
            "UPDATE professeur SET UserId = ? WHERE Id = ? AND UserId IS NULL",
            (user_id, professeur_id),
            tx=tx,
        )
    return user_id
