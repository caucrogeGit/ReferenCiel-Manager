# pyright: strict
"""Politique de mot de passe (ADR-014 T1) : source **unique** adossée au cœur Forge.

Toute création ou réinitialisation de mot de passe passe par ici, pour appliquer la
même règle (`core.auth.validate_new_password` : longueur minimale et maximale). On
n'ajoute pas de règle maison divergente ; on centralise l'appel au cœur et on
traduit son exception en message affichable.
"""
from __future__ import annotations

from core.auth.exceptions import InvalidNewPasswordError
from core.auth.reset import validate_new_password


def valider_mot_de_passe(password: str) -> str | None:
    """Retourne `None` si le mot de passe respecte la politique du cœur, sinon un
    message d'erreur affichable (français, fourni par le cœur)."""
    try:
        validate_new_password(password)
    except InvalidNewPasswordError as exc:
        return str(exc)
    return None
