"""Tests de la persistance MFA (ADR-014) sans backend BDD.

`core.database` est mocké : on vérifie que le secret TOTP est stocké **tel quel**
(déjà chiffré par l'opt-in, jamais en clair), que les requêtes ciblent les bonnes
tables, et que le remplacement des codes de secours purge avant d'insérer. CI-safe
(ADR-006).
"""
from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import pytest
from forge_mvc_mfa import AuthMfaFactor, AuthMfaRecoveryCode

from mvc.models import mfa_model as m


def test_insert_factor_persiste_le_secret_chiffre(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, Any] = {}

    def fake_insert(sql: str, params: Sequence[Any] = ()) -> int:
        captured["sql"] = sql
        captured["params"] = tuple(params)
        return 1

    monkeypatch.setattr(m, "insert", fake_insert)
    factor = AuthMfaFactor(
        id=None, user_id=7, factor_type="totp", totp_secret="enc:XXXX", status="pending"
    )
    m.insert_factor(factor)

    assert "INSERT INTO auth_mfa_factors" in captured["sql"]
    assert "enc:XXXX" in captured["params"]  # secret déjà chiffré, tel quel
    assert 7 in captured["params"]


def test_has_active_totp_filtre_statut_et_compte(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, Any] = {}

    def fake_fetch_one(sql: str, params: Sequence[Any] = ()) -> dict[str, Any] | None:
        captured["sql"] = sql
        captured["params"] = tuple(params)
        return {"id": 1}

    monkeypatch.setattr(m, "fetch_one", fake_fetch_one)
    assert m.has_active_totp(7) is True
    assert "auth_mfa_factors" in captured["sql"]
    assert "status = ?" in captured["sql"]
    assert 7 in captured["params"]


def test_get_active_totp_factors_normalise(monkeypatch: pytest.MonkeyPatch) -> None:
    row: dict[str, Any] = {
        "id": 1, "user_id": 7, "factor_type": "totp", "totp_secret": "enc:x",
        "status": "active", "label": None, "confirmed_at": None,
        "last_used_at": None, "created_at": None, "updated_at": None,
    }

    def fake_fetch_all(sql: str, params: Sequence[Any] = ()) -> list[dict[str, Any]]:
        return [row]

    monkeypatch.setattr(m, "fetch_all", fake_fetch_all)
    factors = m.get_active_totp_factors(7)

    assert len(factors) == 1
    assert factors[0].user_id == 7
    assert factors[0].status == "active"


def test_remplacer_recovery_codes_purge_puis_insere(monkeypatch: pytest.MonkeyPatch) -> None:
    execs: list[str] = []
    inserts: list[tuple[Any, ...]] = []

    def fake_execute(sql: str, params: Sequence[Any] = ()) -> int:
        execs.append(sql)
        return 0

    def fake_insert(sql: str, params: Sequence[Any] = ()) -> int:
        inserts.append(tuple(params))
        return 1

    monkeypatch.setattr(m, "execute", fake_execute)
    monkeypatch.setattr(m, "insert", fake_insert)
    records = [
        AuthMfaRecoveryCode(id=None, user_id=7, code_hash="h1"),
        AuthMfaRecoveryCode(id=None, user_id=7, code_hash="h2"),
    ]
    m.remplacer_recovery_codes(7, records)

    assert any("DELETE FROM auth_mfa_recovery_codes" in s for s in execs)
    assert len(inserts) == 2
    assert "h1" in inserts[0] and "h2" in inserts[1]


def test_mark_recovery_used_cible_le_hash_non_consomme(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, Any] = {}

    def fake_execute(sql: str, params: Sequence[Any] = ()) -> int:
        captured["sql"] = sql
        captured["params"] = tuple(params)
        return 0

    monkeypatch.setattr(m, "execute", fake_execute)
    m.mark_recovery_used("h1")

    assert "UPDATE auth_mfa_recovery_codes" in captured["sql"]
    assert "used_at" in captured["sql"]
    assert "used_at IS NULL" in captured["sql"]  # ne re-consomme pas un code déjà utilisé
    assert "h1" in captured["params"]
