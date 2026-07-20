-- Migration Forge
-- Version: 20260720123632
-- Name: adr030_savoir_libre
-- ADR-030 : savoirs libres d'une séquence sans référentiel. Liste de texte libre
-- saisie par le professeur (comme les indicateurs de réussite). Types alignés sur
-- la base réelle (Id BIGINT UNSIGNED). FK cascade : purgés avec la séquence.

CREATE TABLE IF NOT EXISTS savoir_libre (
    Id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    Libelle TEXT NOT NULL,
    sequence_id BIGINT UNSIGNED NOT NULL,
    CreatedAt DATETIME NOT NULL,
    UpdatedAt DATETIME NOT NULL,
    PRIMARY KEY (Id),
    INDEX idx_savoir_libre_sequence_id (sequence_id),
    CONSTRAINT fk_savoir_libre_sequence_id
        FOREIGN KEY (sequence_id) REFERENCES sequence (Id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
