-- Migration Forge
-- Version: 20260709113102
-- Name: create_professeur
-- Source: entity Professeur
-- Generated from: /home/roger/Projets/ReferenCiel-Manager/mvc/entities/professeur/professeur.sql
--
-- Review this SQL before running:
-- forge migration:apply

CREATE TABLE IF NOT EXISTS professeur (
    Id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    Nom VARCHAR(100) NOT NULL,
    Prenom VARCHAR(100) NOT NULL,
    UserId BIGINT NULL,
    CreatedAt DATETIME NOT NULL,
    UpdatedAt DATETIME NOT NULL,
    PRIMARY KEY (Id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
