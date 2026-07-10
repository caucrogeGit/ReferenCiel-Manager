-- Migration Forge
-- Version: 20260710112126
-- Name: create_affectation_parcours
-- Source: entity AffectationParcours
-- Generated from: /home/roger/Projets/ReferenCiel-Manager/mvc/entities/affectation_parcours/affectation_parcours.sql
--
-- Review this SQL before running:
-- forge migration:apply

CREATE TABLE IF NOT EXISTS affectation_parcours (
    Id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    DateAffectation DATE NOT NULL,
    Statut VARCHAR(20) NOT NULL,
    version_parcours_id BIGINT UNSIGNED NOT NULL,
    classe_id BIGINT UNSIGNED NOT NULL,
    professeur_id BIGINT UNSIGNED NOT NULL,
    CreatedAt DATETIME NOT NULL,
    UpdatedAt DATETIME NOT NULL,
    PRIMARY KEY (Id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Contraintes FK (copiees de mvc/entities/relations.sql).
ALTER TABLE affectation_parcours
    ADD CONSTRAINT fk_affectation_parcours_version_parcours_id
    FOREIGN KEY (version_parcours_id)
    REFERENCES version_parcours (Id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT;

ALTER TABLE affectation_parcours
    ADD CONSTRAINT fk_affectation_parcours_classe_id
    FOREIGN KEY (classe_id)
    REFERENCES classe (Id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT;

ALTER TABLE affectation_parcours
    ADD CONSTRAINT fk_affectation_parcours_professeur_id
    FOREIGN KEY (professeur_id)
    REFERENCES professeur (Id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT;

-- Pivot m2m eleves (sous-ensemble optionnel). DDL corrige a la main (F28 : INT en
-- BIGINT UNSIGNED, ENGINE ajoute, REFERENCES en Id).
CREATE TABLE IF NOT EXISTS affectation_parcours_eleve (
    Id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    affectation_parcours_id BIGINT UNSIGNED NOT NULL,
    eleve_id BIGINT UNSIGNED NOT NULL,
    PRIMARY KEY (Id),
    UNIQUE KEY uq_affectation_parcours_eleve (affectation_parcours_id, eleve_id),
    INDEX idx_ape_affectation (affectation_parcours_id),
    INDEX idx_ape_eleve (eleve_id),
    CONSTRAINT fk_ape_affectation_parcours_id
        FOREIGN KEY (affectation_parcours_id) REFERENCES affectation_parcours (Id) ON DELETE CASCADE,
    CONSTRAINT fk_ape_eleve_id
        FOREIGN KEY (eleve_id) REFERENCES eleve (Id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
