-- Migration Forge
-- Version: 20260709221805
-- Name: create_groupe
-- Source: entity Groupe
-- Generated from: /home/roger/Projets/ReferenCiel-Manager/mvc/entities/groupe/groupe.sql
--
-- Review this SQL before running:
-- forge migration:apply

CREATE TABLE IF NOT EXISTS groupe (
    Id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    Nom VARCHAR(100) NOT NULL,
    classe_id BIGINT UNSIGNED NOT NULL,
    CreatedAt DATETIME NOT NULL,
    UpdatedAt DATETIME NOT NULL,
    PRIMARY KEY (Id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Contrainte FK many_to_one vers Classe (copiee de mvc/entities/relations.sql).
ALTER TABLE groupe
    ADD CONSTRAINT fk_groupe_classe_id
    FOREIGN KEY (classe_id)
    REFERENCES classe (Id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT;

-- Table pivot many_to_many Groupe <-> Eleve (jonction pure).
-- DDL CORRIGE a la main : sync:relations genere les colonnes en INT, mais les PK
-- visees (groupe.Id, eleve.Id) sont BIGINT UNSIGNED -> FK incompatible (errno 150),
-- et la clause ENGINE manque. Voir retour-013 (F28). Types alignes ci-dessous.
CREATE TABLE IF NOT EXISTS groupe_eleve (
    Id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    groupe_id BIGINT UNSIGNED NOT NULL,
    eleve_id BIGINT UNSIGNED NOT NULL,
    PRIMARY KEY (Id),
    UNIQUE KEY uq_groupe_eleve (groupe_id, eleve_id),
    INDEX idx_groupe_eleve_groupe_id (groupe_id),
    INDEX idx_groupe_eleve_eleve_id (eleve_id),
    CONSTRAINT fk_groupe_eleve_groupe_id
        FOREIGN KEY (groupe_id)
        REFERENCES groupe (Id)
        ON DELETE CASCADE,
    CONSTRAINT fk_groupe_eleve_eleve_id
        FOREIGN KEY (eleve_id)
        REFERENCES eleve (Id)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
