-- Migration Forge
-- Version: 20260710115047
-- Name: create_tentative_qcm
-- Source: entity TentativeQCM
-- Generated from: /home/roger/Projets/ReferenCiel-Manager/mvc/entities/tentative_qcm/tentative_qcm.sql
--
-- Review this SQL before running:
-- forge migration:apply

CREATE TABLE IF NOT EXISTS tentative_qcm (
    Id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    NumeroTentative INT NOT NULL,
    Score INT NOT NULL,
    Validee BOOLEAN NOT NULL,
    DateTentative DATETIME NOT NULL,
    progression_palier_id BIGINT UNSIGNED NOT NULL,
    CreatedAt DATETIME NOT NULL,
    UpdatedAt DATETIME NOT NULL,
    PRIMARY KEY (Id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Reponses de l eleve par question (justesse figee a la soumission : est_correcte).
CREATE TABLE IF NOT EXISTS reponse_qcm (
    Id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    EstCorrecte BOOLEAN NOT NULL,
    tentative_id BIGINT UNSIGNED NOT NULL,
    question_id BIGINT UNSIGNED NOT NULL,
    choix_id BIGINT UNSIGNED NOT NULL,
    CreatedAt DATETIME NOT NULL,
    UpdatedAt DATETIME NOT NULL,
    PRIMARY KEY (Id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Contraintes FK (copiees de mvc/entities/relations.sql).
ALTER TABLE tentative_qcm
    ADD CONSTRAINT fk_tentative_qcm_progression_palier_id
    FOREIGN KEY (progression_palier_id) REFERENCES progression_palier (Id) ON DELETE CASCADE ON UPDATE RESTRICT;

ALTER TABLE reponse_qcm
    ADD CONSTRAINT fk_reponse_qcm_tentative_id
    FOREIGN KEY (tentative_id) REFERENCES tentative_qcm (Id) ON DELETE CASCADE ON UPDATE RESTRICT;

ALTER TABLE reponse_qcm
    ADD CONSTRAINT fk_reponse_qcm_question_id
    FOREIGN KEY (question_id) REFERENCES question_qcm (Id) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE reponse_qcm
    ADD CONSTRAINT fk_reponse_qcm_choix_id
    FOREIGN KEY (choix_id) REFERENCES choix_qcm (Id) ON DELETE RESTRICT ON UPDATE RESTRICT;

-- Unicite metier : numero de tentative unique par progression, une reponse par question et tentative.
ALTER TABLE tentative_qcm
    ADD CONSTRAINT uq_tentative_qcm_progression_numero UNIQUE (progression_palier_id, NumeroTentative);

ALTER TABLE reponse_qcm
    ADD CONSTRAINT uq_reponse_qcm_tentative_question UNIQUE (tentative_id, question_id);
