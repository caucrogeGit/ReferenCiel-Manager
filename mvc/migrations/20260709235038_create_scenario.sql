-- Migration Forge
-- Version: 20260709235038
-- Name: create_scenario
-- Source: entity Scenario
-- Generated from: /home/roger/Projets/ReferenCiel-Manager/mvc/entities/scenario/scenario.sql
--
-- Review this SQL before running:
-- forge migration:apply

CREATE TABLE IF NOT EXISTS scenario (
    Id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    Titre VARCHAR(200) NOT NULL,
    Intention TEXT NOT NULL,
    Objectifs TEXT NULL,
    Statut VARCHAR(20) NOT NULL,
    Version VARCHAR(20) NOT NULL,
    referentiel_id BIGINT UNSIGNED NOT NULL,
    auteur_id BIGINT UNSIGNED NOT NULL,
    CreatedAt DATETIME NOT NULL,
    UpdatedAt DATETIME NOT NULL,
    PRIMARY KEY (Id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Contraintes FK (copiees de mvc/entities/relations.sql).
ALTER TABLE scenario
    ADD CONSTRAINT fk_scenario_referentiel_id
    FOREIGN KEY (referentiel_id)
    REFERENCES referentiel_niveau_classe (Id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT;

ALTER TABLE scenario
    ADD CONSTRAINT fk_scenario_auteur_id
    FOREIGN KEY (auteur_id)
    REFERENCES professeur (Id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT;

-- Tables pivots m2m (competences visees, criteres retenus). DDL corrige a la main
-- (F28 : colonnes INT en BIGINT UNSIGNED, clause ENGINE ajoutee, REFERENCES en Id).
CREATE TABLE IF NOT EXISTS scenario_competence (
    Id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    scenario_id BIGINT UNSIGNED NOT NULL,
    competence_id BIGINT UNSIGNED NOT NULL,
    PRIMARY KEY (Id),
    UNIQUE KEY uq_scenario_competence (scenario_id, competence_id),
    INDEX idx_scenario_competence_scenario_id (scenario_id),
    INDEX idx_scenario_competence_competence_id (competence_id),
    CONSTRAINT fk_scenario_competence_scenario_id
        FOREIGN KEY (scenario_id) REFERENCES scenario (Id) ON DELETE CASCADE,
    CONSTRAINT fk_scenario_competence_competence_id
        FOREIGN KEY (competence_id) REFERENCES competence (Id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS scenario_critere (
    Id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    scenario_id BIGINT UNSIGNED NOT NULL,
    critere_observable_id BIGINT UNSIGNED NOT NULL,
    PRIMARY KEY (Id),
    UNIQUE KEY uq_scenario_critere (scenario_id, critere_observable_id),
    INDEX idx_scenario_critere_scenario_id (scenario_id),
    INDEX idx_scenario_critere_critere_observable_id (critere_observable_id),
    CONSTRAINT fk_scenario_critere_scenario_id
        FOREIGN KEY (scenario_id) REFERENCES scenario (Id) ON DELETE CASCADE,
    CONSTRAINT fk_scenario_critere_critere_observable_id
        FOREIGN KEY (critere_observable_id) REFERENCES critere_observable (Id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
