-- Migration Forge
-- Version: 20260710162647
-- Name: create_professeur_compte_user_fk
-- Lie un Professeur du socle a un compte users (1 vers 1, nullable), symetrique
-- de eleve. La colonne UserId (BIGINT) passe INT pour matcher users.id (INT),
-- devient UNIQUE (au plus un compte par professeur) puis recoit la FK.
-- ON DELETE SET NULL : supprimer le compte delie le professeur sans effacer sa fiche.

-- Aligne le type de UserId sur users.id (INT signe) pour autoriser la FK.
ALTER TABLE professeur MODIFY UserId INT NULL;

-- Un compte au plus par professeur (les valeurs NULL restent multiples en MariaDB).
ALTER TABLE professeur ADD UNIQUE KEY uk_professeur_user_id (UserId);

-- Cle etrangere vers le socle auth users.
ALTER TABLE professeur
    ADD CONSTRAINT fk_professeur_user_id
    FOREIGN KEY (UserId) REFERENCES users(id) ON DELETE SET NULL;
