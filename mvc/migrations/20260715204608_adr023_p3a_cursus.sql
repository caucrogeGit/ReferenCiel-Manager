-- Migration Forge
-- Version: 20260715204608
-- Name: adr023_p3a_cursus
-- ADR-023 phase 3a : Cursus + CursusEtape, le pivot academique.
-- Un Cursus est un chemin vers une certification (modalite scolaire/apprentissage),
-- ordonne en CursusEtape sur des FormationNiveau. Demonstration : le meme Bac Pro
-- CIEL par deux chemins (scolaire via 2TNE, apprentissage direct en CIEL).
-- Idempotent (IF NOT EXISTS, INSERT IGNORE, sous-requetes par Code).

-- 1) Table Cursus.
CREATE TABLE IF NOT EXISTS cursus (
    Id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    Code VARCHAR(50) NOT NULL,
    UNIQUE KEY uk_cursus_code (Code),
    Libelle VARCHAR(200) NOT NULL,
    Modalite VARCHAR(30) NOT NULL,
    Statut VARCHAR(20) NOT NULL,
    Description TEXT NULL,
    certification_cible_id BIGINT UNSIGNED NOT NULL,
    CreatedAt DATETIME NOT NULL,
    UpdatedAt DATETIME NOT NULL,
    PRIMARY KEY (Id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

ALTER TABLE cursus DROP FOREIGN KEY IF EXISTS fk_cursus_certification_cible_id;
ALTER TABLE cursus
    ADD CONSTRAINT fk_cursus_certification_cible_id
        FOREIGN KEY (certification_cible_id) REFERENCES certification (Id)
        ON DELETE RESTRICT ON UPDATE RESTRICT;

-- 2) Table CursusEtape (+ unique : une FormationNiveau au plus une fois par cursus,
-- sert aussi d'index de tete a la FK cursus_id).
CREATE TABLE IF NOT EXISTS cursus_etape (
    Id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    Ordre INT NOT NULL,
    Obligatoire BOOLEAN NOT NULL,
    ConditionEntree VARCHAR(255) NULL,
    ConditionSortie VARCHAR(255) NULL,
    cursus_id BIGINT UNSIGNED NOT NULL,
    formation_niveau_id BIGINT UNSIGNED NOT NULL,
    CreatedAt DATETIME NOT NULL,
    UpdatedAt DATETIME NOT NULL,
    PRIMARY KEY (Id),
    UNIQUE KEY uq_cursus_etape (cursus_id, formation_niveau_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

ALTER TABLE cursus_etape DROP FOREIGN KEY IF EXISTS fk_cursus_etape_cursus_id;
ALTER TABLE cursus_etape
    ADD CONSTRAINT fk_cursus_etape_cursus_id
        FOREIGN KEY (cursus_id) REFERENCES cursus (Id)
        ON DELETE CASCADE ON UPDATE RESTRICT;

ALTER TABLE cursus_etape DROP FOREIGN KEY IF EXISTS fk_cursus_etape_formation_niveau_id;
ALTER TABLE cursus_etape
    ADD CONSTRAINT fk_cursus_etape_formation_niveau_id
        FOREIGN KEY (formation_niveau_id) REFERENCES formation_niveau (Id)
        ON DELETE RESTRICT ON UPDATE RESTRICT;

-- 3) FormationNiveau CIEL / SECONDE_PRO (entree directe en specialite = apprentissage).
INSERT IGNORE INTO formation_niveau (formation_id, niveau_classe_id, Code, Libelle, OrdreIndicatif, CreatedAt, UpdatedAt)
    SELECT f.Id, nc.Id, '2CIEL', 'Seconde Bac Pro CIEL', 1, NOW(), NOW()
    FROM formation f JOIN niveau_classe nc ON nc.Code = 'SECONDE_PRO'
    WHERE f.Code = 'BACPRO-CIEL';

-- 4) Cursus vers le Bac Pro CIEL : deux modalites.
INSERT IGNORE INTO cursus (Code, Libelle, Modalite, Statut, certification_cible_id, CreatedAt, UpdatedAt)
    SELECT 'BAC-PRO-CIEL-SCOLAIRE', 'Bac Pro CIEL - voie scolaire', 'SCOLAIRE', 'actif', c.Id, NOW(), NOW()
    FROM certification c WHERE c.Code = 'BAC-PRO-CIEL';
INSERT IGNORE INTO cursus (Code, Libelle, Modalite, Statut, certification_cible_id, CreatedAt, UpdatedAt)
    SELECT 'BAC-PRO-CIEL-APPRENTISSAGE', 'Bac Pro CIEL - apprentissage', 'APPRENTISSAGE', 'actif', c.Id, NOW(), NOW()
    FROM certification c WHERE c.Code = 'BAC-PRO-CIEL';

-- 5) Etapes du cursus scolaire : 2TNE/2nde -> CIEL/1re -> CIEL/Term.
INSERT IGNORE INTO cursus_etape (cursus_id, formation_niveau_id, Ordre, Obligatoire, CreatedAt, UpdatedAt)
    SELECT cu.Id, fn.Id, 1, 1, NOW(), NOW() FROM cursus cu JOIN formation_niveau fn ON fn.Code='2TNE'  WHERE cu.Code='BAC-PRO-CIEL-SCOLAIRE';
INSERT IGNORE INTO cursus_etape (cursus_id, formation_niveau_id, Ordre, Obligatoire, CreatedAt, UpdatedAt)
    SELECT cu.Id, fn.Id, 2, 1, NOW(), NOW() FROM cursus cu JOIN formation_niveau fn ON fn.Code='1CIEL' WHERE cu.Code='BAC-PRO-CIEL-SCOLAIRE';
INSERT IGNORE INTO cursus_etape (cursus_id, formation_niveau_id, Ordre, Obligatoire, CreatedAt, UpdatedAt)
    SELECT cu.Id, fn.Id, 3, 1, NOW(), NOW() FROM cursus cu JOIN formation_niveau fn ON fn.Code='TCIEL' WHERE cu.Code='BAC-PRO-CIEL-SCOLAIRE';

-- 6) Etapes du cursus apprentissage : CIEL/2nde -> CIEL/1re -> CIEL/Term.
INSERT IGNORE INTO cursus_etape (cursus_id, formation_niveau_id, Ordre, Obligatoire, CreatedAt, UpdatedAt)
    SELECT cu.Id, fn.Id, 1, 1, NOW(), NOW() FROM cursus cu JOIN formation_niveau fn ON fn.Code='2CIEL' WHERE cu.Code='BAC-PRO-CIEL-APPRENTISSAGE';
INSERT IGNORE INTO cursus_etape (cursus_id, formation_niveau_id, Ordre, Obligatoire, CreatedAt, UpdatedAt)
    SELECT cu.Id, fn.Id, 2, 1, NOW(), NOW() FROM cursus cu JOIN formation_niveau fn ON fn.Code='1CIEL' WHERE cu.Code='BAC-PRO-CIEL-APPRENTISSAGE';
INSERT IGNORE INTO cursus_etape (cursus_id, formation_niveau_id, Ordre, Obligatoire, CreatedAt, UpdatedAt)
    SELECT cu.Id, fn.Id, 3, 1, NOW(), NOW() FROM cursus cu JOIN formation_niveau fn ON fn.Code='TCIEL' WHERE cu.Code='BAC-PRO-CIEL-APPRENTISSAGE';
