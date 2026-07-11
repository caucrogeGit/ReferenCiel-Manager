"""Tests de la politique de mot de passe et du flux de reset (ADR-013 T1) sans BDD.

`core.database` est mocké : on vérifie que la politique du cœur est appliquée, et
que le model ne fait circuler que le **hash** du token (jamais le token brut) et cible
les bonnes tables. CI-safe (ADR-006).
"""
from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime, timezone
from typing import Any

import pytest

from core.auth.tokens import AuthToken, hash_auth_token
from mvc.models import password_reset_model as m
from mvc.services.password_policy import valider_mot_de_passe


def test_politique_refuse_mot_de_passe_trop_court() -> None:
    message = valider_mot_de_passe("abc")
    assert message is not None
    assert "8" in message  # message du cœur : au moins 8 caractères


def test_politique_accepte_mot_de_passe_conforme() -> None:
    assert valider_mot_de_passe("motdepasse-solide") is None


def test_get_token_record_cherche_par_hash_pas_par_token_brut(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}

    def fake_fetch_one(sql: str, params: Sequence[Any] = ()) -> dict[str, Any] | None:
        captured["sql"] = sql
        captured["params"] = tuple(params)
        return None

    monkeypatch.setattr(m, "fetch_one", fake_fetch_one)
    m.get_token_record("un-token-brut")

    assert "FROM auth_tokens" in captured["sql"]
    assert "token_hash = ?" in captured["sql"]
    # C'est bien le HASH qui est requêté, jamais le token brut.
    assert captured["params"] == (hash_auth_token("un-token-brut"),)
    assert "un-token-brut" not in captured["params"]


def test_enregistrer_token_ne_stocke_que_le_hash(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, Any] = {}

    def fake_insert(sql: str, params: Sequence[Any] = ()) -> int:
        captured["sql"] = sql
        captured["params"] = tuple(params)
        return 1

    monkeypatch.setattr(m, "insert", fake_insert)
    token = AuthToken(
        user_id=7,
        purpose="password_reset",
        token_hash="deadbeef",
        expires_at=datetime(2026, 7, 11, tzinfo=timezone.utc),
        created_at=datetime(2026, 7, 11, tzinfo=timezone.utc),
    )
    m.enregistrer_token(token)

    assert "INSERT INTO auth_tokens" in captured["sql"]
    assert "deadbeef" in captured["params"]  # le hash
    assert 7 in captured["params"]  # user_id


def test_get_user_by_email_cible_users(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, Any] = {}

    def fake_fetch_one(sql: str, params: Sequence[Any] = ()) -> dict[str, Any] | None:
        captured["sql"] = sql
        captured["params"] = tuple(params)
        return {"id": 1, "email": "a@b.c", "is_active": 1}

    monkeypatch.setattr(m, "fetch_one", fake_fetch_one)
    row = m.get_user_by_email("a@b.c")

    assert "FROM users" in captured["sql"]
    assert captured["params"] == ("a@b.c",)
    assert row is not None and row["id"] == 1
