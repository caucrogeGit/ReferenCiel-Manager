-- Migration Forge
-- Version: 20260710141532
-- Name: create_eleve_compte_user_fk
-- Lie un Eleve du socle a un compte users (1 vers 1, nullable) et ajoute le
-- role eleve. La colonne UserId existait deja (BIGINT) sans contrainte : on la
-- ramene a INT pour matcher users.id (INT), on la rend UNIQUE (au plus un compte
-- par eleve) puis on pose la FK. ON DELETE SET NULL : supprimer le compte
-- delie l eleve sans effacer ses donnees pedagogiques.

-- Role eleve (slug aligne sur le contrat mvc/security/rbac.json).
INSERT INTO roles (slug, name) VALUES ('eleve', 'Eleve');

-- Aligne le type de UserId sur users.id (INT signe) pour autoriser la FK.
ALTER TABLE eleve MODIFY UserId INT NULL;

-- Un compte au plus par eleve (les valeurs NULL restent multiples en MariaDB).
ALTER TABLE eleve ADD UNIQUE KEY uk_eleve_user_id (UserId);

-- Cle etrangere vers le socle auth users.
ALTER TABLE eleve
    ADD CONSTRAINT fk_eleve_user_id
    FOREIGN KEY (UserId) REFERENCES users(id) ON DELETE SET NULL;
