CREATE TABLE IF NOT EXISTS sequence (
    Id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    Identifiant VARCHAR(100) NOT NULL,
    UNIQUE KEY uk_sequence_identifiant (Identifiant),
    Titre VARCHAR(200) NOT NULL,
    Presentation TEXT NULL,
    Statut VARCHAR(20) NOT NULL,
    ActiviteGlissante BOOLEAN NOT NULL,
    OrdreImpose BOOLEAN NOT NULL,
    niveau_classe_id BIGINT UNSIGNED NOT NULL,
    CreatedAt DATETIME NOT NULL,
    UpdatedAt DATETIME NOT NULL,
    PRIMARY KEY (Id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
