-- Migration Forge
-- Version: 20260709214547
-- Name: create_inscription_eleve
-- Source: entity InscriptionEleve
-- Generated from: /home/roger/Projets/ReferenCiel-Manager/mvc/entities/inscription_eleve/inscription_eleve.sql
--
-- Review this SQL before running:
-- forge migration:apply

CREATE TABLE IF NOT EXISTS inscription_eleve (
    Id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    DateInscription DATE NULL,
    eleve_id BIGINT UNSIGNED NOT NULL,
    classe_id BIGINT UNSIGNED NOT NULL,
    annee_scolaire_id BIGINT UNSIGNED NOT NULL,
    CreatedAt DATETIME NOT NULL,
    UpdatedAt DATETIME NOT NULL,
    PRIMARY KEY (Id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Contraintes FK (copiees de mvc/entities/relations.sql) : ajoutees ici tant que
-- migration:make ne les integre pas encore (retour-010 F22, encore partiel).
ALTER TABLE inscription_eleve
    ADD CONSTRAINT fk_inscription_eleve_eleve_id
    FOREIGN KEY (eleve_id)
    REFERENCES eleve (Id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT;

ALTER TABLE inscription_eleve
    ADD CONSTRAINT fk_inscription_eleve_classe_id
    FOREIGN KEY (classe_id)
    REFERENCES classe (Id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT;

ALTER TABLE inscription_eleve
    ADD CONSTRAINT fk_inscription_eleve_annee_scolaire_id
    FOREIGN KEY (annee_scolaire_id)
    REFERENCES annee_scolaire (Id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT;

-- Unicité métier (dictionnaire) : un élève inscrit une seule fois par (classe, année).
ALTER TABLE inscription_eleve
    ADD CONSTRAINT uq_inscription_eleve_eleve_classe_annee
    UNIQUE (eleve_id, classe_id, annee_scolaire_id);
