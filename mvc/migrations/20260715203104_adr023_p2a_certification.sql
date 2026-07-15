-- Migration Forge
-- Version: 20260715203104
-- Name: adr023_p2a_certification
-- ADR-023 phase 2a : Certification (diplome/titre) separee de la formation.
--   - table certification ;
--   - formation.certification_id (nullable) : une formation « prepare » 0..1
--     certification (2TNE n'en prepare aucune, CIEL prepare le Bac Pro CIEL) ;
--   - seed : Bac Pro CIEL + rattachement de la formation CIEL.
-- Idempotent (IF [NOT] EXISTS, INSERT IGNORE, UPDATE cible).

-- 1) Table Certification (schema genere par sync:entity).
CREATE TABLE IF NOT EXISTS certification (
    Id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    Code VARCHAR(50) NOT NULL,
    UNIQUE KEY uk_certification_code (Code),
    Libelle VARCHAR(200) NOT NULL,
    Type VARCHAR(40) NOT NULL,
    NiveauRncp VARCHAR(10) NULL,
    AutoriteCertificatrice VARCHAR(200) NULL,
    Statut VARCHAR(20) NOT NULL,
    CreatedAt DATETIME NOT NULL,
    UpdatedAt DATETIME NOT NULL,
    PRIMARY KEY (Id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2) Lien formation -> certification (0..1, SET NULL si la certification part).
ALTER TABLE formation ADD COLUMN IF NOT EXISTS certification_id BIGINT UNSIGNED NULL AFTER Intitule;
ALTER TABLE formation DROP FOREIGN KEY IF EXISTS fk_formation_certification_id;
ALTER TABLE formation
    ADD CONSTRAINT fk_formation_certification_id
        FOREIGN KEY (certification_id) REFERENCES certification (Id)
        ON DELETE SET NULL ON UPDATE RESTRICT;

-- 3) Seed : Bac Pro CIEL.
INSERT IGNORE INTO certification (Code, Libelle, Type, NiveauRncp, AutoriteCertificatrice, Statut, CreatedAt, UpdatedAt)
    VALUES ('BAC-PRO-CIEL',
            'Baccalauréat professionnel Cybersécurité, Informatique et réseaux, Électronique',
            'BAC_PRO', '4', 'Ministère de l''Éducation nationale', 'actif', NOW(), NOW());

-- 4) La formation CIEL prepare le Bac Pro CIEL.
UPDATE formation f
    JOIN certification c ON c.Code = 'BAC-PRO-CIEL'
    SET f.certification_id = c.Id
    WHERE f.Code = 'BACPRO-CIEL';
