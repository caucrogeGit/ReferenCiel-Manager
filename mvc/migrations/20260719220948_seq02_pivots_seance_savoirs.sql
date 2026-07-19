-- Migration Forge
-- Version: 20260719220948
-- Name: seq02_pivots_seance_savoirs
-- SEQ-02 : trois tables de rattachement de la séance et des savoirs associés.
--   savoir_associe    : liste libre de savoirs rattachés à une séquence.
--   seance_competence : compétences travaillées/évaluées par une séance (rôle).
--   seance_critere    : critères observables retenus pour une séance.
-- Types alignés sur la base réelle (Id BIGINT UNSIGNED, FK BIGINT UNSIGNED),
-- pas sur relations.sql (id INT). Côté référentiel (competence, critere) la
-- suppression est CASCADE, comme scenario_competence/scenario_critere, pour que
-- la ré-import d'un référentiel qui purge son contenu ne soit pas bloquée.

CREATE TABLE IF NOT EXISTS savoir_associe (
    Id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    Libelle TEXT NOT NULL,
    sequence_id BIGINT UNSIGNED NOT NULL,
    CreatedAt DATETIME NOT NULL,
    UpdatedAt DATETIME NOT NULL,
    PRIMARY KEY (Id),
    INDEX idx_savoir_associe_sequence_id (sequence_id),
    CONSTRAINT fk_savoir_associe_sequence_id
        FOREIGN KEY (sequence_id) REFERENCES sequence (Id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS seance_competence (
    Id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    seance_id BIGINT UNSIGNED NOT NULL,
    competence_id BIGINT UNSIGNED NOT NULL,
    Role VARCHAR(20) NOT NULL,
    CreatedAt DATETIME NOT NULL,
    UpdatedAt DATETIME NOT NULL,
    PRIMARY KEY (Id),
    UNIQUE KEY uq_seance_competence (seance_id, competence_id),
    INDEX idx_seance_competence_seance_id (seance_id),
    INDEX idx_seance_competence_competence_id (competence_id),
    CONSTRAINT fk_seance_competence_seance_id
        FOREIGN KEY (seance_id) REFERENCES seance (Id) ON DELETE CASCADE,
    CONSTRAINT fk_seance_competence_competence_id
        FOREIGN KEY (competence_id) REFERENCES competence (Id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS seance_critere (
    Id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    seance_id BIGINT UNSIGNED NOT NULL,
    critere_observable_id BIGINT UNSIGNED NOT NULL,
    CreatedAt DATETIME NOT NULL,
    UpdatedAt DATETIME NOT NULL,
    PRIMARY KEY (Id),
    UNIQUE KEY uq_seance_critere (seance_id, critere_observable_id),
    INDEX idx_seance_critere_seance_id (seance_id),
    INDEX idx_seance_critere_critere_observable_id (critere_observable_id),
    CONSTRAINT fk_seance_critere_seance_id
        FOREIGN KEY (seance_id) REFERENCES seance (Id) ON DELETE CASCADE,
    CONSTRAINT fk_seance_critere_critere_observable_id
        FOREIGN KEY (critere_observable_id) REFERENCES critere_observable (Id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
