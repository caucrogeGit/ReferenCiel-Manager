# pyright: strict
"""Socle d'authentification `users` (Forge auth:init) : loader par id.

`charger_utilisateur(user_id)` est le pendant « par id » de `load_user_by_email`
(auth_controller). Il sert de `user_loader` a l'AuthMiddleware — qui valide alors
l'existence ET l'activite du sujet, fermant une session orpheline (ADR-080) — et
au provider contrat Jinja (is_authenticated / can autoritaires, F55).

Retourne la ligne du compte (id, email, password_hash, is_active), contrat
minimal de `normalize_auth_user`, ou None si l'id ne pointe aucun compte.
"""
from typing import Any

from core.database.db import fetch_one


def charger_utilisateur(user_id: int) -> "dict[str, Any] | None":
    return fetch_one(
        "SELECT id, email, password_hash, is_active FROM users WHERE id = ?",
        (user_id,),
    )
