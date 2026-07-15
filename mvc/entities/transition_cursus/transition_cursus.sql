CREATE TABLE IF NOT EXISTS transition_cursus (
    Id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    TypeTransition VARCHAR(40) NOT NULL,
    Conditions VARCHAR(255) NULL,
    DateDebutValidite DATE NULL,
    DateFinValidite DATE NULL,
    formation_niveau_source_id BIGINT UNSIGNED NOT NULL,
    formation_niveau_cible_id BIGINT UNSIGNED NOT NULL,
    CreatedAt DATETIME NOT NULL,
    UpdatedAt DATETIME NOT NULL,
    PRIMARY KEY (Id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
