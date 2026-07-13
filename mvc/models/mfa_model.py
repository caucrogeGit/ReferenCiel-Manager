# pyright: strict
"""MFA (ADR-015) : persistance des facteurs TOTP et des codes de secours.

Orchestration **pure** déléguée à l'opt-in `forge_mvc_mfa` ; ce module ne fait que
la persistance en SQL visible et paramétré. Le secret TOTP est stocké **chiffré**
(l'opt-in le préfixe `enc:`), les codes de secours **hashés** (SHA-256). Les
normaliseurs de l'opt-in font le pont ligne SQL → objet.
"""
from __future__ import annotations

from typing import Any

from forge_mvc_mfa import (
    MFA_FACTOR_TOTP,
    MFA_STATUS_ACTIVE,
    MFA_STATUS_PENDING,
    AuthMfaFactor,
    AuthMfaRecoveryCode,
    normalize_mfa_factor,
    normalize_recovery_code_record,
)

from core.database.db import execute, fetch_all, fetch_one, insert

_FACTOR_COLS = (
    "id, user_id, factor_type, totp_secret, status, label, "
    "confirmed_at, last_used_at, created_at, updated_at"
)
_RECOVERY_COLS = "id, user_id, code_hash, used_at, created_at, updated_at"


# --- Facteurs TOTP ---------------------------------------------------------


def insert_factor(factor: AuthMfaFactor) -> int:
    """Insère un facteur (statut `pending`), secret déjà chiffré par l'opt-in."""
    return insert(
        "INSERT INTO auth_mfa_factors "
        "(user_id, factor_type, totp_secret, status, label, created_at, updated_at) "
        "VALUES (?, ?, ?, ?, ?, NOW(), NOW())",
        (factor.user_id, factor.factor_type, factor.totp_secret, factor.status, factor.label),
    )


def activate_factor(factor_id: int) -> None:
    """Passe un facteur de `pending` à `active` (après confirmation du code)."""
    execute(
        "UPDATE auth_mfa_factors SET status = ?, confirmed_at = NOW(), updated_at = NOW() "
        "WHERE id = ?",
        (MFA_STATUS_ACTIVE, factor_id),
    )


def get_pending_totp_factor(user_id: int) -> AuthMfaFactor | None:
    """Le dernier facteur TOTP en attente de confirmation pour ce compte."""
    row = fetch_one(
        f"SELECT {_FACTOR_COLS} FROM auth_mfa_factors "
        "WHERE user_id = ? AND factor_type = ? AND status = ? ORDER BY id DESC LIMIT 1",
        (user_id, MFA_FACTOR_TOTP, MFA_STATUS_PENDING),
    )
    return normalize_mfa_factor(row) if row is not None else None


def get_active_totp_factors(user_id: int) -> list[AuthMfaFactor]:
    """Les facteurs TOTP actifs du compte (pour `is_mfa_enabled` / le challenge)."""
    rows: list[dict[str, Any]] = fetch_all(
        f"SELECT {_FACTOR_COLS} FROM auth_mfa_factors "
        "WHERE user_id = ? AND factor_type = ? AND status = ?",
        (user_id, MFA_FACTOR_TOTP, MFA_STATUS_ACTIVE),
    )
    return [normalize_mfa_factor(r) for r in rows]


def has_active_totp(user_id: int) -> bool:
    """Vrai si le compte a au moins un facteur TOTP actif (MFA active)."""
    return (
        fetch_one(
            "SELECT id FROM auth_mfa_factors "
            "WHERE user_id = ? AND factor_type = ? AND status = ? LIMIT 1",
            (user_id, MFA_FACTOR_TOTP, MFA_STATUS_ACTIVE),
        )
        is not None
    )


def touch_factor_last_used(factor_id: int) -> None:
    """Met à jour `last_used_at` après une vérification TOTP réussie."""
    execute(
        "UPDATE auth_mfa_factors SET last_used_at = NOW(), updated_at = NOW() WHERE id = ?",
        (factor_id,),
    )


def desactiver_mfa(user_id: int) -> None:
    """Désactive complètement la MFA d'un compte : facteurs + codes de secours."""
    execute("DELETE FROM auth_mfa_factors WHERE user_id = ?", (user_id,))
    execute("DELETE FROM auth_mfa_recovery_codes WHERE user_id = ?", (user_id,))


# --- Codes de secours ------------------------------------------------------


def remplacer_recovery_codes(user_id: int, records: list[AuthMfaRecoveryCode]) -> None:
    """Remplace les codes de secours du compte (purge puis insertion des hash)."""
    execute("DELETE FROM auth_mfa_recovery_codes WHERE user_id = ?", (user_id,))
    for rec in records:
        insert(
            "INSERT INTO auth_mfa_recovery_codes (user_id, code_hash, created_at, updated_at) "
            "VALUES (?, ?, NOW(), NOW())",
            (rec.user_id, rec.code_hash),
        )


def get_unused_recovery_codes(user_id: int) -> list[AuthMfaRecoveryCode]:
    """Les codes de secours non encore consommés (pour le challenge)."""
    rows: list[dict[str, Any]] = fetch_all(
        f"SELECT {_RECOVERY_COLS} FROM auth_mfa_recovery_codes "
        "WHERE user_id = ? AND used_at IS NULL",
        (user_id,),
    )
    return [normalize_recovery_code_record(r) for r in rows]


def count_unused_recovery(user_id: int) -> int:
    """Nombre de codes de secours restants."""
    row = fetch_one(
        "SELECT COUNT(*) AS n FROM auth_mfa_recovery_codes WHERE user_id = ? AND used_at IS NULL",
        (user_id,),
    )
    return int(row["n"]) if row is not None else 0


def mark_recovery_used(code_hash: str) -> None:
    """Marque un code de secours comme consommé (après usage au challenge)."""
    execute(
        "UPDATE auth_mfa_recovery_codes SET used_at = NOW(), updated_at = NOW() "
        "WHERE code_hash = ? AND used_at IS NULL",
        (code_hash,),
    )
