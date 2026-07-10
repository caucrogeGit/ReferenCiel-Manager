-- Migration Forge
-- Version: 20260710114248
-- Name: create_qcm
-- Source: entity QCM
-- Generated from: /home/roger/Projets/ReferenCiel-Manager/mvc/entities/qcm/qcm.sql
--
-- Review this SQL before running:
-- forge migration:apply

CREATE TABLE IF NOT EXISTS qcm (
    Id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    FormatReponse TEXT NULL,
    SeuilValidation VARCHAR(20) NOT NULL,
    palier_id BIGINT UNSIGNED NOT NULL,
    CreatedAt DATETIME NOT NULL,
    UpdatedAt DATETIME NOT NULL,
    PRIMARY KEY (Id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Questions et choix du QCM (definition, corrige fusionne via bonne_reponse).
CREATE TABLE IF NOT EXISTS question_qcm (
    Id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    Numero INT NOT NULL,
    Enonce TEXT NOT NULL,
    BonneReponse VARCHAR(5) NOT NULL,
    qcm_id BIGINT UNSIGNED NOT NULL,
    CreatedAt DATETIME NOT NULL,
    UpdatedAt DATETIME NOT NULL,
    PRIMARY KEY (Id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS choix_qcm (
    Id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    Lettre VARCHAR(5) NOT NULL,
    Texte VARCHAR(255) NOT NULL,
    question_id BIGINT UNSIGNED NOT NULL,
    CreatedAt DATETIME NOT NULL,
    UpdatedAt DATETIME NOT NULL,
    PRIMARY KEY (Id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Contraintes FK (copiees de mvc/entities/relations.sql). Contenu possede par le parent.
ALTER TABLE qcm
    ADD CONSTRAINT fk_qcm_palier_id
    FOREIGN KEY (palier_id) REFERENCES palier (Id) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE question_qcm
    ADD CONSTRAINT fk_question_qcm_qcm_id
    FOREIGN KEY (qcm_id) REFERENCES qcm (Id) ON DELETE CASCADE ON UPDATE RESTRICT;

ALTER TABLE choix_qcm
    ADD CONSTRAINT fk_choix_qcm_question_id
    FOREIGN KEY (question_id) REFERENCES question_qcm (Id) ON DELETE CASCADE ON UPDATE RESTRICT;

-- Unicite metier : un QCM par palier, numero unique par QCM, lettre unique par question.
ALTER TABLE qcm
    ADD CONSTRAINT uq_qcm_palier UNIQUE (palier_id);

ALTER TABLE question_qcm
    ADD CONSTRAINT uq_question_qcm_numero UNIQUE (qcm_id, Numero);

ALTER TABLE choix_qcm
    ADD CONSTRAINT uq_choix_qcm_lettre UNIQUE (question_id, Lettre);
