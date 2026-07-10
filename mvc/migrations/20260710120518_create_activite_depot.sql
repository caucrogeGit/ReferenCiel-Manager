-- Migration Forge
-- Version: 20260710120518
-- Name: create_activite_depot
-- Source: entity Activite
-- Generated from: /home/roger/Projets/ReferenCiel-Manager/mvc/entities/activite/activite.sql
--
-- Review this SQL before running:
-- forge migration:apply

CREATE TABLE IF NOT EXISTS activite (
    Id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    Objectif TEXT NULL,
    Fichier VARCHAR(255) NULL,
    palier_id BIGINT UNSIGNED NOT NULL,
    CreatedAt DATETIME NOT NULL,
    UpdatedAt DATETIME NOT NULL,
    PRIMARY KEY (Id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Depot de l eleve (execution) : un fichier par depot, plusieurs depots possibles.
CREATE TABLE IF NOT EXISTS depot_eleve (
    Id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    Fichier VARCHAR(255) NOT NULL,
    Commentaire TEXT NULL,
    DateDepot DATETIME NOT NULL,
    progression_palier_id BIGINT UNSIGNED NOT NULL,
    activite_id BIGINT UNSIGNED NOT NULL,
    CreatedAt DATETIME NOT NULL,
    UpdatedAt DATETIME NOT NULL,
    PRIMARY KEY (Id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Contraintes FK (copiees de mvc/entities/relations.sql).
ALTER TABLE activite
    ADD CONSTRAINT fk_activite_palier_id
    FOREIGN KEY (palier_id) REFERENCES palier (Id) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE depot_eleve
    ADD CONSTRAINT fk_depot_eleve_progression_palier_id
    FOREIGN KEY (progression_palier_id) REFERENCES progression_palier (Id) ON DELETE CASCADE ON UPDATE RESTRICT;

ALTER TABLE depot_eleve
    ADD CONSTRAINT fk_depot_eleve_activite_id
    FOREIGN KEY (activite_id) REFERENCES activite (Id) ON DELETE RESTRICT ON UPDATE RESTRICT;
