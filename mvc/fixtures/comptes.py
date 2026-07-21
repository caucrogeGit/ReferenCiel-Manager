"""Fixture callable : comptes de démonstration (users + rôles). ADR-078.

Un administrateur, trois professeurs et deux élèves authentifiables. Les
professeurs/élèves sans compte (UserId NULL) restent gérés par l'administration.
Mots de passe de démo uniquement (la politique réelle ADR-014/015 s'applique en
fonctionnement)."""
from forge_mvc_fixtures import Fixture
from core.auth.password import hash_password
from core.database import db


class ComptesFixture(Fixture):
    tables = ("users", "user_roles")

    def load(self) -> None:
        for email, mdp, role in [
            ("admin@referenciel.local", "admin1234", "admin"),
            ("prof@referenciel.local", "prof1234", "professeur"),
            ("prof2@referenciel.local", "prof1234", "professeur"),
            ("prof3@referenciel.local", "prof1234", "professeur"),
            ("eleve@referenciel.local", "eleve1234", "eleve"),
            ("eleve2@referenciel.local", "eleve1234", "eleve"),
        ]:
            uid = db.insert("INSERT INTO users (email, password_hash, is_active) VALUES (?, ?, 1)",
                            (email, hash_password(mdp)))
            db.execute("INSERT INTO user_roles (user_id, role_id) SELECT ?, id FROM roles WHERE slug = ?",
                       (uid, role))
