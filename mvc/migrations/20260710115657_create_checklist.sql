-- Migration Forge
-- Version: 20260710115657
-- Name: create_checklist
-- Source: entity Checklist
-- Generated from: /home/roger/Projets/ReferenCiel-Manager/mvc/entities/checklist/checklist.sql
--
-- Review this SQL before running:
-- forge migration:apply

CREATE TABLE IF NOT EXISTS checklist (
    Id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    DecisionFinale LONGTEXT NULL,
    palier_id BIGINT UNSIGNED NOT NULL,
    CreatedAt DATETIME NOT NULL,
    UpdatedAt DATETIME NOT NULL,
    PRIMARY KEY (Id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Definition : sections et items (points a verifier).
CREATE TABLE IF NOT EXISTS section_checklist (
    Id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    Numero INT NOT NULL,
    Titre VARCHAR(200) NOT NULL,
    checklist_id BIGINT UNSIGNED NOT NULL,
    CreatedAt DATETIME NOT NULL,
    UpdatedAt DATETIME NOT NULL,
    PRIMARY KEY (Id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS item_checklist (
    Id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    Libelle TEXT NOT NULL,
    section_id BIGINT UNSIGNED NOT NULL,
    CreatedAt DATETIME NOT NULL,
    UpdatedAt DATETIME NOT NULL,
    PRIMARY KEY (Id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Execution : case cochee par eleve et/ou professeur, dans la progression de l eleve.
CREATE TABLE IF NOT EXISTS item_coche (
    Id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    CocheEleve BOOLEAN NOT NULL,
    CocheProfesseur BOOLEAN NOT NULL,
    item_id BIGINT UNSIGNED NOT NULL,
    progression_palier_id BIGINT UNSIGNED NOT NULL,
    CreatedAt DATETIME NOT NULL,
    UpdatedAt DATETIME NOT NULL,
    PRIMARY KEY (Id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Contraintes FK (copiees de mvc/entities/relations.sql).
ALTER TABLE checklist
    ADD CONSTRAINT fk_checklist_palier_id
    FOREIGN KEY (palier_id) REFERENCES palier (Id) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE section_checklist
    ADD CONSTRAINT fk_section_checklist_checklist_id
    FOREIGN KEY (checklist_id) REFERENCES checklist (Id) ON DELETE CASCADE ON UPDATE RESTRICT;

ALTER TABLE item_checklist
    ADD CONSTRAINT fk_item_checklist_section_id
    FOREIGN KEY (section_id) REFERENCES section_checklist (Id) ON DELETE CASCADE ON UPDATE RESTRICT;

ALTER TABLE item_coche
    ADD CONSTRAINT fk_item_coche_item_id
    FOREIGN KEY (item_id) REFERENCES item_checklist (Id) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE item_coche
    ADD CONSTRAINT fk_item_coche_progression_palier_id
    FOREIGN KEY (progression_palier_id) REFERENCES progression_palier (Id) ON DELETE CASCADE ON UPDATE RESTRICT;

-- Unicite metier : numero unique par checklist, un cochage par item et progression.
ALTER TABLE section_checklist
    ADD CONSTRAINT uq_section_checklist_numero UNIQUE (checklist_id, Numero);

ALTER TABLE item_coche
    ADD CONSTRAINT uq_item_coche_item_progression UNIQUE (item_id, progression_palier_id);
