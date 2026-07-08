-- Migration Forge
-- Version: 20260708133600
-- Name: create_niveau_classe
-- Source: entity NiveauClasse
-- Generated from: /home/roger/Projets/ReferenCiel-Manager/mvc/entities/niveau_classe/niveau_classe.sql
--
-- Review this SQL before running:
-- forge migration:apply

CREATE TABLE IF NOT EXISTS niveau_classe (
    Id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    Code VARCHAR(20) NOT NULL,
    UNIQUE KEY uk_niveau_classe_code (Code),
    Intitule VARCHAR(150) NOT NULL,
    CreatedAt DATETIME NOT NULL,
    UpdatedAt DATETIME NOT NULL,
    PRIMARY KEY (Id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
