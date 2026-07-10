-- Migration Forge
-- Version: 20260710113008
-- Name: create_progression
-- Source: entity ProgressionEleve
-- Generated from: /home/roger/Projets/ReferenCiel-Manager/mvc/entities/progression_eleve/progression_eleve.sql
--
-- Review this SQL before running:
-- forge migration:apply

CREATE TABLE IF NOT EXISTS progression_eleve (
    Id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    Statut VARCHAR(20) NOT NULL,
    DateDebut DATE NULL,
    eleve_id BIGINT UNSIGNED NOT NULL,
    affectation_parcours_id BIGINT UNSIGNED NOT NULL,
    CreatedAt DATETIME NOT NULL,
    UpdatedAt DATETIME NOT NULL,
    PRIMARY KEY (Id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Etat par palier (non_commence / en_cours / valide / bloque).
CREATE TABLE IF NOT EXISTS progression_palier (
    Id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    Statut VARCHAR(20) NOT NULL,
    progression_eleve_id BIGINT UNSIGNED NOT NULL,
    palier_id BIGINT UNSIGNED NOT NULL,
    CreatedAt DATETIME NOT NULL,
    UpdatedAt DATETIME NOT NULL,
    PRIMARY KEY (Id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Contraintes FK (copiees de mvc/entities/relations.sql).
ALTER TABLE progression_eleve
    ADD CONSTRAINT fk_progression_eleve_eleve_id
    FOREIGN KEY (eleve_id) REFERENCES eleve (Id) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE progression_eleve
    ADD CONSTRAINT fk_progression_eleve_affectation_parcours_id
    FOREIGN KEY (affectation_parcours_id) REFERENCES affectation_parcours (Id) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE progression_palier
    ADD CONSTRAINT fk_progression_palier_progression_eleve_id
    FOREIGN KEY (progression_eleve_id) REFERENCES progression_eleve (Id) ON DELETE CASCADE ON UPDATE RESTRICT;

ALTER TABLE progression_palier
    ADD CONSTRAINT fk_progression_palier_palier_id
    FOREIGN KEY (palier_id) REFERENCES palier (Id) ON DELETE RESTRICT ON UPDATE RESTRICT;

-- Unicite metier : une progression par eleve et par affectation, un etat par palier.
ALTER TABLE progression_eleve
    ADD CONSTRAINT uq_progression_eleve_eleve_affectation
    UNIQUE (eleve_id, affectation_parcours_id);

ALTER TABLE progression_palier
    ADD CONSTRAINT uq_progression_palier_progression_palier
    UNIQUE (progression_eleve_id, palier_id);
