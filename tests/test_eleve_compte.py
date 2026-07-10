"""Tests de la gestion des comptes élèves (socle admin) sans backend BDD.

`core.database` et le hash sont mockés : on vérifie que `creer_compte_eleve`
effectue bien les **trois** écritures (compte users, rôle eleve, lien fiche) dans
la transaction, et la validation d'email. CI-safe (ADR-006).
"""
from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import pytest

from mvc.models import eleve_compte_model as m


def test_email_est_valide_rejette_identifiant_nu() -> None:
    assert m.email_est_valide("prof@referenciel.local")
    assert not m.email_est_valide("admin")        # identifiant nu refusé
    assert not m.email_est_valide("a@b")          # domaine sans point
    assert not m.email_est_valide("a b@c.fr")     # espace interdit


def test_creer_compte_eleve_cree_pose_role_et_lie(monkeypatch: pytest.MonkeyPatch) -> None:
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
        return 55  # id du compte créé

    def fake_execute(sql: str, params: Sequence[Any] = (), *, tx: Any = None) -> int:
        calls.append(("execute", sql, tuple(params)))
        return 1

    monkeypatch.setattr(m, "insert", fake_insert)
    monkeypatch.setattr(m, "execute", fake_execute)

    user_id = m.creer_compte_eleve(7, "jane@x.fr", "motdepasse")
    assert user_id == 55

    ins = next(c for c in calls if c[0] == "insert")
    assert "INSERT INTO users" in ins[1]
    assert "HASH::motdepasse" in ins[2]  # mot de passe hashé, jamais en clair

    role = next(c for c in calls if "user_roles" in c[1])
    assert role[2] == (55, "eleve")  # rôle eleve posé pour le nouveau compte

    lien = next(c for c in calls if "UPDATE eleve" in c[1])
    assert lien[2] == (55, 7)  # fiche 7 liée au compte 55
    assert "UserId IS NULL" in lien[1]  # n'écrase pas un lien existant
