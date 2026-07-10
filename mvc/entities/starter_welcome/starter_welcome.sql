CREATE TABLE IF NOT EXISTS starter_welcome (
    Id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    Identifiant VARCHAR(100) NOT NULL,
    UNIQUE KEY uk_starter_welcome_identifiant (Identifiant),
    Titre VARCHAR(200) NOT NULL,
    Presentation TEXT NULL,
    niveau_classe_id BIGINT UNSIGNED NOT NULL,
    CreatedAt DATETIME NOT NULL,
    UpdatedAt DATETIME NOT NULL,
    PRIMARY KEY (Id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
