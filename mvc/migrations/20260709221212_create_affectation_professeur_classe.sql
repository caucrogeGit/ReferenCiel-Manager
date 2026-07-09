-- Migration Forge
-- Version: 20260709221212
-- Name: create_affectation_professeur_classe
-- Source: entity AffectationProfesseurClasse
-- Generated from: /home/roger/Projets/ReferenCiel-Manager/mvc/entities/affectation_professeur_classe/affectation_professeur_classe.sql
--
-- Review this SQL before running:
-- forge migration:apply

CREATE TABLE IF NOT EXISTS affectation_professeur_classe (
    Id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    Role VARCHAR(100) NULL,
    professeur_id BIGINT UNSIGNED NOT NULL,
    classe_id BIGINT UNSIGNED NOT NULL,
    annee_scolaire_id BIGINT UNSIGNED NOT NULL,
    CreatedAt DATETIME NOT NULL,
    UpdatedAt DATETIME NOT NULL,
    PRIMARY KEY (Id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Contraintes FK (copiees de mvc/entities/relations.sql) : ajoutees ici tant que
-- migration:make ne les integre pas encore (retour-010 F22, encore partiel).
ALTER TABLE affectation_professeur_classe
    ADD CONSTRAINT fk_affectation_professeur_classe_professeur_id
    FOREIGN KEY (professeur_id)
    REFERENCES professeur (Id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT;

ALTER TABLE affectation_professeur_classe
    ADD CONSTRAINT fk_affectation_professeur_classe_classe_id
    FOREIGN KEY (classe_id)
    REFERENCES classe (Id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT;

ALTER TABLE affectation_professeur_classe
    ADD CONSTRAINT fk_affectation_professeur_classe_annee_scolaire_id
    FOREIGN KEY (annee_scolaire_id)
    REFERENCES annee_scolaire (Id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT;

-- Unicite metier (dictionnaire) : un professeur affecte une seule fois par (classe, annee).
ALTER TABLE affectation_professeur_classe
    ADD CONSTRAINT uq_affectation_prof_classe_annee
    UNIQUE (professeur_id, classe_id, annee_scolaire_id);
