CREATE TABLE IF NOT EXISTS evaluation_activite (
    Id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    DateEvaluation DATETIME NOT NULL,
    Appreciation TEXT NULL,
    Production TEXT NULL,
    AideApportee TEXT NULL,
    progression_seance_id BIGINT UNSIGNED NOT NULL,
    activite_id BIGINT UNSIGNED NULL,
    element_seance_id BIGINT UNSIGNED NULL,
    professeur_id BIGINT UNSIGNED NOT NULL,
    CreatedAt DATETIME NOT NULL,
    UpdatedAt DATETIME NOT NULL,
    PRIMARY KEY (Id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
