-- Migration Forge
-- Version: 20260715213019
-- Name: adr023_p4_transition_cursus
-- ADR-023 phase 4 : TransitionCursus (orientations et passerelles entre etapes).
-- Une transition relie deux FormationNiveau (source -> cible) avec un type et une
-- validite. Distincte de RelationFormation (structure nationale) : ici, les
-- passages possibles d'un eleve. Seed : orientation 2TNE/2nde -> CIEL/1re.
-- Idempotent (IF NOT EXISTS, INSERT IGNORE, sous-requetes par Code).

-- 1) Table TransitionCursus (+ unique : sert aussi d'index de tete a la FK source ;
-- la FK cible aura son propre index auto).
CREATE TABLE IF NOT EXISTS transition_cursus (
    Id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    TypeTransition VARCHAR(40) NOT NULL,
    Conditions VARCHAR(255) NULL,
    DateDebutValidite DATE NULL,
    DateFinValidite DATE NULL,
    formation_niveau_source_id BIGINT UNSIGNED NOT NULL,
    formation_niveau_cible_id BIGINT UNSIGNED NOT NULL,
    CreatedAt DATETIME NOT NULL,
    UpdatedAt DATETIME NOT NULL,
    PRIMARY KEY (Id),
    UNIQUE KEY uq_transition_cursus (formation_niveau_source_id, formation_niveau_cible_id, TypeTransition)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

ALTER TABLE transition_cursus DROP FOREIGN KEY IF EXISTS fk_transition_cursus_formation_niveau_source_id;
ALTER TABLE transition_cursus
    ADD CONSTRAINT fk_transition_cursus_formation_niveau_source_id
        FOREIGN KEY (formation_niveau_source_id) REFERENCES formation_niveau (Id)
        ON DELETE CASCADE ON UPDATE RESTRICT;

ALTER TABLE transition_cursus DROP FOREIGN KEY IF EXISTS fk_transition_cursus_formation_niveau_cible_id;
ALTER TABLE transition_cursus
    ADD CONSTRAINT fk_transition_cursus_formation_niveau_cible_id
        FOREIGN KEY (formation_niveau_cible_id) REFERENCES formation_niveau (Id)
        ON DELETE CASCADE ON UPDATE RESTRICT;

-- 2) Seed : orientation de la 2nde commune vers la 1re CIEL.
INSERT IGNORE INTO transition_cursus (formation_niveau_source_id, formation_niveau_cible_id, TypeTransition, Conditions, CreatedAt, UpdatedAt)
    SELECT s.Id, c.Id, 'ORIENTATION', 'Choix de la spécialité CIEL en fin de 2nde famille TNE', NOW(), NOW()
    FROM formation_niveau s JOIN formation_niveau c ON c.Code = '1CIEL'
    WHERE s.Code = '2TNE';
