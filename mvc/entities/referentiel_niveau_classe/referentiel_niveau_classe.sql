CREATE TABLE IF NOT EXISTS referentiel_niveau_classe (
    Id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    Identifiant VARCHAR(100) NOT NULL,
    UNIQUE KEY uk_referentiel_niveau_classe_identifiant (Identifiant),
    Version VARCHAR(20) NOT NULL,
    Statut VARCHAR(20) NOT NULL,
    ImporteLe DATETIME NOT NULL,
    formation_id BIGINT UNSIGNED NOT NULL,
    CreatedAt DATETIME NOT NULL,
    UpdatedAt DATETIME NOT NULL,
    PRIMARY KEY (Id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
