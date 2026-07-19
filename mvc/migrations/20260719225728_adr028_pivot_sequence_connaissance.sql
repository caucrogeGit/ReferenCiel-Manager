-- Migration Forge
-- Version: 20260719225728
-- Name: adr028_pivot_sequence_connaissance
-- ADR-028 : lien Séquence ↔ Connaissance. Porte les données pédagogiques propres
-- à la séquence, distinctes du référentiel : NiveauCible (≠ niveau officiel de la
-- connaissance), Statut (prerequis/apportee/mobilisee/consolidee), Commentaire.
-- Types alignés sur la base réelle (Id BIGINT UNSIGNED). FK CASCADE côté séquence
-- ET côté connaissance : le lien est purgé si la connaissance disparaît d'un
-- référentiel réimporté, comme scenario_competence.

CREATE TABLE IF NOT EXISTS sequence_connaissance (
    Id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    sequence_id BIGINT UNSIGNED NOT NULL,
    connaissance_id BIGINT UNSIGNED NOT NULL,
    NiveauCible INT NULL,
    Statut VARCHAR(20) NULL,
    Commentaire TEXT NULL,
    CreatedAt DATETIME NOT NULL,
    UpdatedAt DATETIME NOT NULL,
    PRIMARY KEY (Id),
    UNIQUE KEY uq_sequence_connaissance (sequence_id, connaissance_id),
    INDEX idx_sequence_connaissance_sequence_id (sequence_id),
    INDEX idx_sequence_connaissance_connaissance_id (connaissance_id),
    CONSTRAINT fk_sequence_connaissance_sequence_id
        FOREIGN KEY (sequence_id) REFERENCES sequence (Id) ON DELETE CASCADE,
    CONSTRAINT fk_sequence_connaissance_connaissance_id
        FOREIGN KEY (connaissance_id) REFERENCES connaissance (Id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
