-- Migration Forge
-- Version: 20260710104053
-- Name: create_starter_welcome
-- Source: entity StarterWelcome
-- Generated from: /home/roger/Projets/ReferenCiel-Manager/mvc/entities/starter_welcome/starter_welcome.sql
--
-- Review this SQL before running:
-- forge migration:apply

CREATE TABLE IF NOT EXISTS starter_welcome (
    Id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    Identifiant VARCHAR(100) NOT NULL,
    UNIQUE KEY uk_starter_welcome_identifiant (Identifiant),
    Titre VARCHAR(200) NOT NULL,
    Presentation TEXT NULL,
    niveau_classe_id BIGINT UNSIGNED NOT NULL,
    CreatedAt DATETIME NOT NULL,
    UpdatedAt DATETIME NOT NULL,
    PRIMARY KEY (Id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Entite de version (ADR-011) : versions d un starter.
CREATE TABLE IF NOT EXISTS version_starter (
    Id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    Version VARCHAR(20) NOT NULL,
    Statut VARCHAR(20) NOT NULL,
    ActiviteGlissante BOOLEAN NOT NULL,
    OrdreImpose BOOLEAN NOT NULL,
    starter_id BIGINT UNSIGNED NOT NULL,
    CreatedAt DATETIME NOT NULL,
    UpdatedAt DATETIME NOT NULL,
    PRIMARY KEY (Id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Contraintes FK (copiees de mvc/entities/relations.sql).
ALTER TABLE starter_welcome
    ADD CONSTRAINT fk_starter_welcome_niveau_classe_id
    FOREIGN KEY (niveau_classe_id)
    REFERENCES niveau_classe (Id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT;

ALTER TABLE version_starter
    ADD CONSTRAINT fk_version_starter_starter_id
    FOREIGN KEY (starter_id)
    REFERENCES starter_welcome (Id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT;

-- Unicite metier : une seule version par numero pour un starter donne.
ALTER TABLE version_starter
    ADD CONSTRAINT uq_version_starter_starter_version
    UNIQUE (starter_id, Version);
