CREATE TABLE IF NOT EXISTS formation_niveau (
    Id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    Code VARCHAR(50) NOT NULL,
    UNIQUE KEY uk_formation_niveau_code (Code),
    Libelle VARCHAR(200) NOT NULL,
    OrdreIndicatif INT NOT NULL,
    formation_id BIGINT UNSIGNED NOT NULL,
    niveau_classe_id BIGINT UNSIGNED NOT NULL,
    CreatedAt DATETIME NOT NULL,
    UpdatedAt DATETIME NOT NULL,
    PRIMARY KEY (Id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
