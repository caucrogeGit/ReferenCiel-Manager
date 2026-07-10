-- Migration Forge
-- Version: 20260710110303
-- Name: create_parcours
-- Source: entity Parcours
-- Generated from: /home/roger/Projets/ReferenCiel-Manager/mvc/entities/parcours/parcours.sql
--
-- Review this SQL before running:
-- forge migration:apply

CREATE TABLE IF NOT EXISTS parcours (
    Id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    Titre VARCHAR(200) NOT NULL,
    version_starter_id BIGINT UNSIGNED NOT NULL,
    CreatedAt DATETIME NOT NULL,
    UpdatedAt DATETIME NOT NULL,
    PRIMARY KEY (Id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Version de parcours (ADR-011) et paliers (decoupage, ticket 16).
CREATE TABLE IF NOT EXISTS version_parcours (
    Id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    Version VARCHAR(20) NOT NULL,
    Statut VARCHAR(20) NOT NULL,
    parcours_id BIGINT UNSIGNED NOT NULL,
    CreatedAt DATETIME NOT NULL,
    UpdatedAt DATETIME NOT NULL,
    PRIMARY KEY (Id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS palier (
    Id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    Ordre INT NOT NULL,
    Titre VARCHAR(200) NOT NULL,
    Theme VARCHAR(100) NULL,
    ProductionAttendue VARCHAR(255) NULL,
    DossierTechniqueFichier VARCHAR(255) NOT NULL,
    version_parcours_id BIGINT UNSIGNED NOT NULL,
    CreatedAt DATETIME NOT NULL,
    UpdatedAt DATETIME NOT NULL,
    PRIMARY KEY (Id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Contraintes FK (copiees de mvc/entities/relations.sql).
ALTER TABLE parcours
    ADD CONSTRAINT fk_parcours_version_starter_id
    FOREIGN KEY (version_starter_id)
    REFERENCES version_starter (Id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT;

ALTER TABLE version_parcours
    ADD CONSTRAINT fk_version_parcours_parcours_id
    FOREIGN KEY (parcours_id)
    REFERENCES parcours (Id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT;

ALTER TABLE palier
    ADD CONSTRAINT fk_palier_version_parcours_id
    FOREIGN KEY (version_parcours_id)
    REFERENCES version_parcours (Id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT;

-- Unicite metier : une version par numero de parcours, et ordre unique par version.
ALTER TABLE version_parcours
    ADD CONSTRAINT uq_version_parcours_parcours_version
    UNIQUE (parcours_id, Version);

ALTER TABLE palier
    ADD CONSTRAINT uq_palier_version_ordre
    UNIQUE (version_parcours_id, Ordre);
