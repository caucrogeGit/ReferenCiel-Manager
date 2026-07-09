-- Migration Forge
-- Version: 20260709223454
-- Name: create_referentiel
-- Schema du domaine referentiel niveau-classe (ticket 10).
-- Assemble depuis les entites + relations.sql (partie referentiel).
-- NiveauClasse est reutilisee du socle scolaire (deja en base).


-- ===== Tables du referentiel (12 entites) =====

CREATE TABLE IF NOT EXISTS formation (
    Id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    Code VARCHAR(50) NOT NULL,
    UNIQUE KEY uk_formation_code (Code),
    Intitule VARCHAR(200) NOT NULL,
    CreatedAt DATETIME NOT NULL,
    UpdatedAt DATETIME NOT NULL,
    PRIMARY KEY (Id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS referentiel_niveau_classe (
    Id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    Identifiant VARCHAR(100) NOT NULL,
    UNIQUE KEY uk_referentiel_niveau_classe_identifiant (Identifiant),
    Version VARCHAR(20) NOT NULL,
    Statut VARCHAR(20) NOT NULL,
    ImporteLe DATETIME NOT NULL,
    formation_id BIGINT UNSIGNED NOT NULL,
    niveau_classe_id BIGINT UNSIGNED NOT NULL,
    CreatedAt DATETIME NOT NULL,
    UpdatedAt DATETIME NOT NULL,
    PRIMARY KEY (Id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS pole_activite (
    Id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    Intitule VARCHAR(250) NOT NULL,
    referentiel_id BIGINT UNSIGNED NOT NULL,
    CreatedAt DATETIME NOT NULL,
    UpdatedAt DATETIME NOT NULL,
    PRIMARY KEY (Id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS competence (
    Id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    Code VARCHAR(10) NOT NULL,
    Intitule VARCHAR(250) NOT NULL,
    referentiel_id BIGINT UNSIGNED NOT NULL,
    CreatedAt DATETIME NOT NULL,
    UpdatedAt DATETIME NOT NULL,
    PRIMARY KEY (Id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS activite_professionnelle (
    Id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    Code VARCHAR(20) NOT NULL,
    Intitule VARCHAR(250) NOT NULL,
    ConditionsExercice TEXT NULL,
    referentiel_id BIGINT UNSIGNED NOT NULL,
    pole_id BIGINT UNSIGNED NOT NULL,
    CreatedAt DATETIME NOT NULL,
    UpdatedAt DATETIME NOT NULL,
    PRIMARY KEY (Id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS tache (
    Id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    Ordre INT NOT NULL,
    Libelle TEXT NOT NULL,
    activite_id BIGINT UNSIGNED NOT NULL,
    CreatedAt DATETIME NOT NULL,
    UpdatedAt DATETIME NOT NULL,
    PRIMARY KEY (Id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS resultat_attendu (
    Id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    Code VARCHAR(100) NOT NULL,
    Libelle TEXT NOT NULL,
    activite_id BIGINT UNSIGNED NOT NULL,
    CreatedAt DATETIME NOT NULL,
    UpdatedAt DATETIME NOT NULL,
    PRIMARY KEY (Id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS connaissance (
    Id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    Libelle TEXT NOT NULL,
    NiveauTaxonomique INT NULL,
    competence_id BIGINT UNSIGNED NOT NULL,
    CreatedAt DATETIME NOT NULL,
    UpdatedAt DATETIME NOT NULL,
    PRIMARY KEY (Id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS critere_observable (
    Id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    Code VARCHAR(100) NOT NULL,
    Libelle TEXT NOT NULL,
    competence_id BIGINT UNSIGNED NOT NULL,
    CreatedAt DATETIME NOT NULL,
    UpdatedAt DATETIME NOT NULL,
    PRIMARY KEY (Id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS indicateur_reussite (
    Id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    Code VARCHAR(100) NOT NULL,
    Libelle TEXT NOT NULL,
    Origine VARCHAR(30) NOT NULL,
    RefCode VARCHAR(50) NULL,
    referentiel_id BIGINT UNSIGNED NOT NULL,
    CreatedAt DATETIME NOT NULL,
    UpdatedAt DATETIME NOT NULL,
    PRIMARY KEY (Id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS famille_competence (
    Id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    Code VARCHAR(10) NOT NULL,
    Intitule VARCHAR(250) NOT NULL,
    referentiel_id BIGINT UNSIGNED NOT NULL,
    CreatedAt DATETIME NOT NULL,
    UpdatedAt DATETIME NOT NULL,
    PRIMARY KEY (Id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS source (
    Id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    SourceId VARCHAR(100) NOT NULL,
    SourceType VARCHAR(30) NOT NULL,
    SourceFichier VARCHAR(255) NOT NULL,
    SourceNote TEXT NULL,
    referentiel_id BIGINT UNSIGNED NOT NULL,
    CreatedAt DATETIME NOT NULL,
    UpdatedAt DATETIME NOT NULL,
    PRIMARY KEY (Id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ===== Contraintes de cles etrangeres + tables pivots (m2m) =====

-- Pivots corriges a la main (F28 : INT -> BIGINT UNSIGNED + ENGINE).

ALTER TABLE referentiel_niveau_classe
    ADD CONSTRAINT fk_referentiel_niveau_classe_formation_id
    FOREIGN KEY (formation_id)
    REFERENCES formation (Id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT;

ALTER TABLE referentiel_niveau_classe
    ADD CONSTRAINT fk_referentiel_niveau_classe_niveau_classe_id
    FOREIGN KEY (niveau_classe_id)
    REFERENCES niveau_classe (Id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT;

ALTER TABLE pole_activite
    ADD CONSTRAINT fk_pole_activite_referentiel_id
    FOREIGN KEY (referentiel_id)
    REFERENCES referentiel_niveau_classe (Id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT;

ALTER TABLE activite_professionnelle
    ADD CONSTRAINT fk_activite_professionnelle_referentiel_id
    FOREIGN KEY (referentiel_id)
    REFERENCES referentiel_niveau_classe (Id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT;

ALTER TABLE activite_professionnelle
    ADD CONSTRAINT fk_activite_professionnelle_pole_id
    FOREIGN KEY (pole_id)
    REFERENCES pole_activite (Id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT;

ALTER TABLE tache
    ADD CONSTRAINT fk_tache_activite_id
    FOREIGN KEY (activite_id)
    REFERENCES activite_professionnelle (Id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT;

ALTER TABLE resultat_attendu
    ADD CONSTRAINT fk_resultat_attendu_activite_id
    FOREIGN KEY (activite_id)
    REFERENCES activite_professionnelle (Id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT;

ALTER TABLE competence
    ADD CONSTRAINT fk_competence_referentiel_id
    FOREIGN KEY (referentiel_id)
    REFERENCES referentiel_niveau_classe (Id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT;

ALTER TABLE connaissance
    ADD CONSTRAINT fk_connaissance_competence_id
    FOREIGN KEY (competence_id)
    REFERENCES competence (Id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT;

ALTER TABLE critere_observable
    ADD CONSTRAINT fk_critere_observable_competence_id
    FOREIGN KEY (competence_id)
    REFERENCES competence (Id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT;

ALTER TABLE indicateur_reussite
    ADD CONSTRAINT fk_indicateur_reussite_referentiel_id
    FOREIGN KEY (referentiel_id)
    REFERENCES referentiel_niveau_classe (Id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT;

ALTER TABLE famille_competence
    ADD CONSTRAINT fk_famille_competence_referentiel_id
    FOREIGN KEY (referentiel_id)
    REFERENCES referentiel_niveau_classe (Id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT;

ALTER TABLE source
    ADD CONSTRAINT fk_source_referentiel_id
    FOREIGN KEY (referentiel_id)
    REFERENCES referentiel_niveau_classe (Id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT;

CREATE TABLE IF NOT EXISTS activite_competence (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    activite_professionnelle_id BIGINT UNSIGNED NOT NULL,
    competence_id BIGINT UNSIGNED NOT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_activite_competence (activite_professionnelle_id, competence_id),
    INDEX idx_activite_competence_activite_professionnelle_id (activite_professionnelle_id),
    INDEX idx_activite_competence_competence_id (competence_id),
    CONSTRAINT fk_activite_competence_activite_professionnelle_id
        FOREIGN KEY (activite_professionnelle_id)
        REFERENCES activite_professionnelle (Id)
        ON DELETE CASCADE,
    CONSTRAINT fk_activite_competence_competence_id
        FOREIGN KEY (competence_id)
        REFERENCES competence (Id)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS cc_competence (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    famille_competence_id BIGINT UNSIGNED NOT NULL,
    competence_id BIGINT UNSIGNED NOT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_cc_competence (famille_competence_id, competence_id),
    INDEX idx_cc_competence_famille_competence_id (famille_competence_id),
    INDEX idx_cc_competence_competence_id (competence_id),
    CONSTRAINT fk_cc_competence_famille_competence_id
        FOREIGN KEY (famille_competence_id)
        REFERENCES famille_competence (Id)
        ON DELETE CASCADE,
    CONSTRAINT fk_cc_competence_competence_id
        FOREIGN KEY (competence_id)
        REFERENCES competence (Id)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ===== Unicite composite (codes uniques dans leur perimetre) =====

ALTER TABLE referentiel_niveau_classe
    ADD CONSTRAINT uq_rnc_formation_niveau_version
    UNIQUE (formation_id, niveau_classe_id, version);

ALTER TABLE activite_professionnelle
    ADD CONSTRAINT uq_activite_ref_code
    UNIQUE (referentiel_id, code);

ALTER TABLE competence
    ADD CONSTRAINT uq_competence_ref_code
    UNIQUE (referentiel_id, code);

ALTER TABLE famille_competence
    ADD CONSTRAINT uq_famille_competence_ref_code
    UNIQUE (referentiel_id, code);

ALTER TABLE resultat_attendu
    ADD CONSTRAINT uq_resultat_attendu_activite_code
    UNIQUE (activite_id, code);

ALTER TABLE critere_observable
    ADD CONSTRAINT uq_critere_observable_comp_code
    UNIQUE (competence_id, code);

ALTER TABLE indicateur_reussite
    ADD CONSTRAINT uq_indicateur_ref_code
    UNIQUE (referentiel_id, code);
