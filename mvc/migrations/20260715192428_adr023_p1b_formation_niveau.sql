-- Migration Forge
-- Version: 20260715192428
-- Name: adr023_p1b_formation_niveau
-- ADR-023 phase 1b : introduit FormationNiveau (application d'une formation a un
-- niveau), le vocabulaire NiveauClasse generique, et la formation famille 2TNE.
--   - niveau_classe 2TNE devient SECONDE_PRO (generique) ; ajout PREMIERE_PRO,
--     TERMINALE_PRO ; les classes/parcours existants suivent (meme Id).
--   - formation 2TNE (FAMILLE_METIERS) creee : c'est elle qui portera le
--     referentiel de la 2nde commune (phase 1c).
--   - amorcage des FormationNiveau : 2TNE/2nde, CIEL/1re, CIEL/Term.
-- Idempotent (IF NOT EXISTS, INSERT IGNORE sur Code unique, UPDATE cible).

-- 1) Table FormationNiveau (schema genere par sync:entity).
CREATE TABLE IF NOT EXISTS formation_niveau (
    Id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    Code VARCHAR(50) NOT NULL,
    UNIQUE KEY uk_formation_niveau_code (Code),
    Libelle VARCHAR(200) NOT NULL,
    OrdreIndicatif INT NOT NULL,
    formation_id BIGINT UNSIGNED NOT NULL,
    niveau_classe_id BIGINT UNSIGNED NOT NULL,
    CreatedAt DATETIME NOT NULL,
    UpdatedAt DATETIME NOT NULL,
    PRIMARY KEY (Id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

ALTER TABLE formation_niveau DROP FOREIGN KEY IF EXISTS fk_formation_niveau_formation_id;
ALTER TABLE formation_niveau
    ADD CONSTRAINT fk_formation_niveau_formation_id
        FOREIGN KEY (formation_id) REFERENCES formation (Id)
        ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE formation_niveau DROP FOREIGN KEY IF EXISTS fk_formation_niveau_niveau_classe_id;
ALTER TABLE formation_niveau
    ADD CONSTRAINT fk_formation_niveau_niveau_classe_id
        FOREIGN KEY (niveau_classe_id) REFERENCES niveau_classe (Id)
        ON DELETE RESTRICT ON UPDATE RESTRICT;

-- 2) NiveauClasse devient un vocabulaire generique.
UPDATE niveau_classe SET Code = 'SECONDE_PRO', Intitule = 'Seconde professionnelle'
    WHERE Code = '2TNE';
INSERT IGNORE INTO niveau_classe (Code, Intitule, CreatedAt, UpdatedAt)
    VALUES ('PREMIERE_PRO', 'Premiere professionnelle', NOW(), NOW());
INSERT IGNORE INTO niveau_classe (Code, Intitule, CreatedAt, UpdatedAt)
    VALUES ('TERMINALE_PRO', 'Terminale professionnelle', NOW(), NOW());

-- 3) Formation famille 2TNE (portera le referentiel de la 2nde commune).
INSERT IGNORE INTO formation (Code, Type, Intitule, CreatedAt, UpdatedAt)
    VALUES ('2TNE', 'FAMILLE_METIERS',
            'Metiers des transitions numerique et energetique', NOW(), NOW());

-- 4) Amorcage des FormationNiveau (Code stable = cle metier, INSERT IGNORE).
INSERT IGNORE INTO formation_niveau (formation_id, niveau_classe_id, Code, Libelle, OrdreIndicatif, CreatedAt, UpdatedAt)
    SELECT f.Id, nc.Id, '2TNE',
           'Seconde professionnelle, famille des metiers des transitions numerique et energetique', 1, NOW(), NOW()
    FROM formation f JOIN niveau_classe nc ON nc.Code = 'SECONDE_PRO'
    WHERE f.Code = '2TNE';
INSERT IGNORE INTO formation_niveau (formation_id, niveau_classe_id, Code, Libelle, OrdreIndicatif, CreatedAt, UpdatedAt)
    SELECT f.Id, nc.Id, '1CIEL', 'Premiere Bac Pro CIEL', 2, NOW(), NOW()
    FROM formation f JOIN niveau_classe nc ON nc.Code = 'PREMIERE_PRO'
    WHERE f.Code = 'BACPRO-CIEL';
INSERT IGNORE INTO formation_niveau (formation_id, niveau_classe_id, Code, Libelle, OrdreIndicatif, CreatedAt, UpdatedAt)
    SELECT f.Id, nc.Id, 'TCIEL', 'Terminale Bac Pro CIEL', 3, NOW(), NOW()
    FROM formation f JOIN niveau_classe nc ON nc.Code = 'TERMINALE_PRO'
    WHERE f.Code = 'BACPRO-CIEL';
