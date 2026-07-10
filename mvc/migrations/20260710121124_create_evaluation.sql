-- Migration Forge
-- Version: 20260710121124
-- Name: create_evaluation
-- Source: entity EvaluationActivite
-- Generated from: /home/roger/Projets/ReferenCiel-Manager/mvc/entities/evaluation_activite/evaluation_activite.sql
--
-- Review this SQL before running:
-- forge migration:apply

CREATE TABLE IF NOT EXISTS evaluation_activite (
    Id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    DateEvaluation DATETIME NOT NULL,
    Appreciation TEXT NULL,
    progression_palier_id BIGINT UNSIGNED NOT NULL,
    activite_id BIGINT UNSIGNED NOT NULL,
    professeur_id BIGINT UNSIGNED NOT NULL,
    CreatedAt DATETIME NOT NULL,
    UpdatedAt DATETIME NOT NULL,
    PRIMARY KEY (Id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Evaluation par critere (barme 4 niveaux : non_acquis/en_cours_acquisition/acquis/expert).
CREATE TABLE IF NOT EXISTS evaluation_critere (
    Id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    Niveau VARCHAR(30) NOT NULL,
    evaluation_activite_id BIGINT UNSIGNED NOT NULL,
    critere_id BIGINT UNSIGNED NOT NULL,
    CreatedAt DATETIME NOT NULL,
    UpdatedAt DATETIME NOT NULL,
    PRIMARY KEY (Id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Contraintes FK (copiees de mvc/entities/relations.sql).
ALTER TABLE evaluation_activite
    ADD CONSTRAINT fk_evaluation_activite_progression_palier_id
    FOREIGN KEY (progression_palier_id) REFERENCES progression_palier (Id) ON DELETE CASCADE ON UPDATE RESTRICT;

ALTER TABLE evaluation_activite
    ADD CONSTRAINT fk_evaluation_activite_activite_id
    FOREIGN KEY (activite_id) REFERENCES activite (Id) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE evaluation_activite
    ADD CONSTRAINT fk_evaluation_activite_professeur_id
    FOREIGN KEY (professeur_id) REFERENCES professeur (Id) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE evaluation_critere
    ADD CONSTRAINT fk_evaluation_critere_evaluation_activite_id
    FOREIGN KEY (evaluation_activite_id) REFERENCES evaluation_activite (Id) ON DELETE CASCADE ON UPDATE RESTRICT;

ALTER TABLE evaluation_critere
    ADD CONSTRAINT fk_evaluation_critere_critere_id
    FOREIGN KEY (critere_id) REFERENCES critere_observable (Id) ON DELETE RESTRICT ON UPDATE RESTRICT;

-- Unicite metier : un niveau par critere pour une evaluation donnee.
ALTER TABLE evaluation_critere
    ADD CONSTRAINT uq_evaluation_critere_eval_critere UNIQUE (evaluation_activite_id, critere_id);
