-- Migration Forge
-- Version: 20260707155952
-- Name: create_annee_scolaire
-- Source: entity AnneeScolaire
-- Generated from: /home/roger/Projets/ReferenCiel-Manager/mvc/entities/annee_scolaire/annee_scolaire.sql
--
-- Review this SQL before running:
-- forge migration:apply

CREATE TABLE IF NOT EXISTS annee_scolaire (
    Id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    Libelle VARCHAR(20) NOT NULL,
    UNIQUE KEY uk_annee_scolaire_libelle (Libelle),
    DateDebut DATE NULL,
    DateFin DATE NULL,
    Active BOOLEAN NOT NULL DEFAULT 0,
    CreatedAt DATETIME NOT NULL,
    UpdatedAt DATETIME NOT NULL,
    PRIMARY KEY (Id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
