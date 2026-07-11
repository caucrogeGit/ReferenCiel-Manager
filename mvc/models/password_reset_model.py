# pyright: strict
"""Réinitialisation de mot de passe (ADR-013 T1) : persistance du flux de reset.

Orchestration **pure** déléguée au cœur (`core.auth.reset`) ; ce module ne fait que
la **persistance** en SQL visible et paramétré : écrire le jeton (`auth_tokens`), le
relire par son hash, puis appliquer le nouveau hash (`users.password_hash`) et
marquer le jeton consommé — en une transaction. Aucun token brut n'est stocké : seul
`token_hash` est en base (le cœur ne renvoie le token brut qu'une fois, pour le lien).
"""
from __future__ import annotations

from typing import Any

from core.auth.tokens import AuthToken, hash_auth_token
from core.database.db import execute, fetch_one, insert
from core.database.transaction import transaction


def get_user_by_email(email: str) -> dict[str, Any] | None:
    """Compte actif correspondant à l'email (pour ouvrir une demande de reset)."""
    return fetch_one(
        "SELECT id, email, is_active FROM users WHERE email = ?", (email,)
    )


def enregistrer_token(token: AuthToken) -> int:
    """Persiste le jeton de reset (hash uniquement) dans `auth_tokens`."""
    return insert(
        "INSERT INTO auth_tokens (user_id, purpose, token_hash, expires_at, created_at) "
        "VALUES (?, ?, ?, ?, ?)",
        (token.user_id, token.purpose, token.token_hash, token.expires_at, token.created_at),
    )


def get_token_record(raw_token: str) -> dict[str, Any] | None:
    """Retrouve la ligne `auth_tokens` correspondant à un token brut (via son hash).

    Retourne le dict brut (`user_id`, `purpose`, `token_hash`, `expires_at`,
    `used_at`, `created_at`) que le cœur sait normaliser en `AuthToken`.
    """
    return fetch_one(
        "SELECT user_id, purpose, token_hash, expires_at, used_at, created_at "
        "FROM auth_tokens WHERE token_hash = ?",
        (hash_auth_token(raw_token),),
    )


def appliquer_reset(
    user_id: int, password_hash: str, used_at: Any, token_hash: str
) -> None:
    """Applique le reset en une transaction : nouveau hash + jeton marqué consommé."""
    with transaction() as tx:
        execute(
            "UPDATE users SET password_hash = ?, updated_at = NOW() WHERE id = ?",
            (password_hash, user_id),
            tx=tx,
        )
        execute(
            "UPDATE auth_tokens SET used_at = ? WHERE token_hash = ?",
            (used_at, token_hash),
            tx=tx,
        )
