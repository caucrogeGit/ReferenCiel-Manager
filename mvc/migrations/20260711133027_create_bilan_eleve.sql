-- Migration Forge
-- Version: 20260711133027
-- Name: create_bilan_eleve
-- Source: entity BilanEleve
-- Generated from: mvc/entities/bilan_eleve/bilan_eleve.sql
--
-- Review this SQL before running:
-- forge migration:apply
-- NB commentaires ASCII sobres sans apostrophe (F27, retour-012).

CREATE TABLE IF NOT EXISTS bilan_eleve (
    Id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    AppreciationGlobale TEXT NOT NULL,
    Statut VARCHAR(20) NOT NULL,
    DateBilan DATETIME NOT NULL,
    Synthese LONGTEXT NULL,
    eleve_id BIGINT UNSIGNED NOT NULL,
    professeur_id BIGINT UNSIGNED NOT NULL,
    progression_eleve_id BIGINT UNSIGNED NOT NULL,
    CreatedAt DATETIME NOT NULL,
    UpdatedAt DATETIME NOT NULL,
    PRIMARY KEY (Id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Contraintes FK (copiees de mvc/entities/relations.sql).
ALTER TABLE bilan_eleve
    ADD CONSTRAINT fk_bilan_eleve_eleve_id
    FOREIGN KEY (eleve_id)
    REFERENCES eleve (Id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT;

ALTER TABLE bilan_eleve
    ADD CONSTRAINT fk_bilan_eleve_professeur_id
    FOREIGN KEY (professeur_id)
    REFERENCES professeur (Id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT;

ALTER TABLE bilan_eleve
    ADD CONSTRAINT fk_bilan_eleve_progression_eleve_id
    FOREIGN KEY (progression_eleve_id)
    REFERENCES progression_eleve (Id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT;
