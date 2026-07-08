-- Migration Forge
-- Version: 20260708221219
-- Name: create_classe
-- Source: entity Classe
-- Generated from: /home/roger/Projets/ReferenCiel-Manager/mvc/entities/classe/classe.sql
--
-- Review this SQL before running:
-- forge migration:apply

CREATE TABLE IF NOT EXISTS classe (
    Id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    Code VARCHAR(20) NOT NULL,
    Libelle VARCHAR(150) NULL,
    CreatedAt DATETIME NOT NULL,
    UpdatedAt DATETIME NOT NULL,
    PRIMARY KEY (Id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Relations (mvc/entities/relations.sql) : colonnes FK + contraintes + index.
-- Ajoutées ici car migration:make ne les intègre pas. Les tables cibles
-- (annee_scolaire, niveau_classe) existent déjà.
ALTER TABLE classe
    ADD COLUMN annee_scolaire_id BIGINT UNSIGNED NOT NULL;
ALTER TABLE classe
    ADD CONSTRAINT fk_classe_annee_scolaire_id
    FOREIGN KEY (annee_scolaire_id)
    REFERENCES annee_scolaire (Id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT;
CREATE INDEX idx_classe_annee_scolaire_id ON classe (annee_scolaire_id);

ALTER TABLE classe
    ADD COLUMN niveau_classe_id BIGINT UNSIGNED NOT NULL;
ALTER TABLE classe
    ADD CONSTRAINT fk_classe_niveau_classe_id
    FOREIGN KEY (niveau_classe_id)
    REFERENCES niveau_classe (Id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT;
CREATE INDEX idx_classe_niveau_classe_id ON classe (niveau_classe_id);
