"""Tests de la gestion des comptes professeurs (socle admin) sans backend BDD.

Symétrique de test_eleve_compte : `creer_compte_professeur` effectue les trois
écritures (compte users, rôle professeur, lien fiche), et l'email est validé.
CI-safe (ADR-006).
"""
from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import pytest

from mvc.models import professeur_compte_model as m


def test_email_est_valide_rejette_identifiant_nu() -> None:
    assert m.email_est_valide("prof@referenciel.local")
    assert not m.email_est_valide("admin")
    assert not m.email_est_valide("a@b")


def test_creer_compte_professeur_cree_pose_role_et_lie(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[tuple[str, str, tuple[Any, ...]]] = []

    class FakeTx:
        def __enter__(self) -> "FakeTx":
            return self

        def __exit__(self, *a: object) -> bool:
            return False

    monkeypatch.setattr(m, "transaction", lambda: FakeTx())
    monkeypatch.setattr(m, "hash_password", lambda pw: "HASH::" + pw)

    def fake_insert(sql: str, params: Sequence[Any] = (), *, tx: Any = None) -> int:
        calls.append(("insert", sql, tuple(params)))
        return 60

    def fake_execute(sql: str, params: Sequence[Any] = (), *, tx: Any = None) -> int:
        calls.append(("execute", sql, tuple(params)))
        return 1

    monkeypatch.setattr(m, "insert", fake_insert)
    monkeypatch.setattr(m, "execute", fake_execute)

    user_id = m.creer_compte_professeur(4, "prof@x.fr", "motdepasse")
    assert user_id == 60

    ins = next(c for c in calls if c[0] == "insert")
    assert "INSERT INTO users" in ins[1] and "HASH::motdepasse" in ins[2]

    role = next(c for c in calls if "user_roles" in c[1])
    assert role[2] == (60, "professeur")  # rôle professeur

    lien = next(c for c in calls if "UPDATE professeur" in c[1])
    assert lien[2] == (60, 4)
    assert "UserId IS NULL" in lien[1]
