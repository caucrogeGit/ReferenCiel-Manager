CREATE TABLE IF NOT EXISTS eleve (
    Id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    Nom VARCHAR(100) NOT NULL,
    Prenom VARCHAR(100) NOT NULL,
    Identifiant VARCHAR(100) NULL,
    UNIQUE KEY uk_eleve_identifiant (Identifiant),
    DateNaissance DATE NULL,
    UserId INT NULL,
    UNIQUE KEY uk_eleve_user_id (UserId),
    classe_id BIGINT UNSIGNED NOT NULL,
    CreatedAt DATETIME NOT NULL,
    UpdatedAt DATETIME NOT NULL,
    PRIMARY KEY (Id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
