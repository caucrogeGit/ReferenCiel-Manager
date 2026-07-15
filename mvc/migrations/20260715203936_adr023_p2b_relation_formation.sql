-- Migration Forge
-- Version: 20260715203936
-- Name: adr023_p2b_relation_formation
-- ADR-023 phase 2b : RelationFormation (structure nationale entre formations).
--   - table relation_formation (source, cible, type_relation) + unique composite
--     anti-doublon ;
--   - creation des bacs pros freres de la famille TNE (MELEC, ICCER, MEE, MFER) ;
--   - seed : 2TNE REGROUPE {CIEL, MELEC, ICCER, MEE, MFER}.
-- Cette relation dit la structure, pas le chemin de l'eleve (Cursus, phase 3).
-- Idempotent (IF NOT EXISTS, INSERT IGNORE).

-- 1) Table RelationFormation (+ unique composite : sert aussi d'index de tete a
-- la FK source ; la FK cible aura son propre index auto).
CREATE TABLE IF NOT EXISTS relation_formation (
    Id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    TypeRelation VARCHAR(40) NOT NULL,
    formation_source_id BIGINT UNSIGNED NOT NULL,
    formation_cible_id BIGINT UNSIGNED NOT NULL,
    CreatedAt DATETIME NOT NULL,
    UpdatedAt DATETIME NOT NULL,
    PRIMARY KEY (Id),
    UNIQUE KEY uq_relation_formation (formation_source_id, formation_cible_id, TypeRelation)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

ALTER TABLE relation_formation DROP FOREIGN KEY IF EXISTS fk_relation_formation_formation_source_id;
ALTER TABLE relation_formation
    ADD CONSTRAINT fk_relation_formation_formation_source_id
        FOREIGN KEY (formation_source_id) REFERENCES formation (Id)
        ON DELETE CASCADE ON UPDATE RESTRICT;

ALTER TABLE relation_formation DROP FOREIGN KEY IF EXISTS fk_relation_formation_formation_cible_id;
ALTER TABLE relation_formation
    ADD CONSTRAINT fk_relation_formation_formation_cible_id
        FOREIGN KEY (formation_cible_id) REFERENCES formation (Id)
        ON DELETE CASCADE ON UPDATE RESTRICT;

-- 2) Bacs pros freres de la famille TNE (specialites, sans referentiel a ce stade).
INSERT IGNORE INTO formation (Code, Type, Intitule, CreatedAt, UpdatedAt) VALUES
    ('BACPRO-MELEC', 'SPECIALITE_BAC_PRO', 'Baccalauréat professionnel Métiers de l''électricité et de ses environnements connectés', NOW(), NOW()),
    ('BACPRO-ICCER', 'SPECIALITE_BAC_PRO', 'Baccalauréat professionnel Installateur en chauffage, climatisation et énergies renouvelables', NOW(), NOW()),
    ('BACPRO-MEE',   'SPECIALITE_BAC_PRO', 'Baccalauréat professionnel Maintenance et efficacité énergétique', NOW(), NOW()),
    ('BACPRO-MFER',  'SPECIALITE_BAC_PRO', 'Baccalauréat professionnel Métiers du froid et des énergies renouvelables', NOW(), NOW());

-- 3) 2TNE REGROUPE chaque bac pro de la famille.
INSERT IGNORE INTO relation_formation (formation_source_id, formation_cible_id, TypeRelation, CreatedAt, UpdatedAt)
    SELECT s.Id, c.Id, 'REGROUPE', NOW(), NOW()
    FROM formation s JOIN formation c
        ON c.Code IN ('BACPRO-CIEL', 'BACPRO-MELEC', 'BACPRO-ICCER', 'BACPRO-MEE', 'BACPRO-MFER')
    WHERE s.Code = '2TNE';
