-- Migration Forge
-- Version: 20260709112042
-- Name: create_eleve
-- Source: entity Eleve
-- Generated from: /home/roger/Projets/ReferenCiel-Manager/mvc/entities/eleve/eleve.sql
--
-- Review this SQL before running:
-- forge migration:apply

CREATE TABLE IF NOT EXISTS eleve (
    Id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    Nom VARCHAR(100) NOT NULL,
    Prenom VARCHAR(100) NOT NULL,
    Identifiant VARCHAR(100) NULL,
    UNIQUE KEY uk_eleve_identifiant (Identifiant),
    DateNaissance DATE NULL,
    UserId BIGINT NULL,
    CreatedAt DATETIME NOT NULL,
    UpdatedAt DATETIME NOT NULL,
    PRIMARY KEY (Id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
