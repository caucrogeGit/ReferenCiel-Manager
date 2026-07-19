# pyright: strict
"""Tests de la politique de mot de passe (ADR-014 T1).

Le service est une façade sur `core.auth.validate_new_password` : on vérifie le
contrat (None si conforme, message affichable sinon) sans recopier les bornes
exactes du cœur, pour ne pas coupler les tests à ses constantes privées.
"""
from __future__ import annotations

from mvc.services.password_policy import valider_mot_de_passe


def test_mot_de_passe_conforme() -> None:
    assert valider_mot_de_passe("correct-horse-battery") is None


def test_mot_de_passe_vide_refuse() -> None:
    message = valider_mot_de_passe("")
    assert isinstance(message, str)
    assert "mot de passe" in message


def test_mot_de_passe_trop_court_refuse() -> None:
    message = valider_mot_de_passe("court")
    assert isinstance(message, str)
    assert "mot de passe" in message


def test_mot_de_passe_trop_long_refuse() -> None:
    message = valider_mot_de_passe("x" * 1000)
    assert isinstance(message, str)
    assert "mot de passe" in message
