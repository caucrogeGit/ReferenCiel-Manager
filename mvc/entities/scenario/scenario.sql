CREATE TABLE IF NOT EXISTS scenario (
    Id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    Titre VARCHAR(200) NOT NULL,
    Intention TEXT NOT NULL,
    Objectifs TEXT NULL,
    DescriptionContexte TEXT NULL,
    Problematique TEXT NULL,
    MaterielsLogiciels TEXT NULL,
    LiensAssocies TEXT NULL,
    EspacesFormation TEXT NULL,
    Statut VARCHAR(20) NOT NULL,
    Version VARCHAR(20) NOT NULL,
    CoIntervention BOOLEAN NOT NULL DEFAULT 0,
    referentiel_id BIGINT UNSIGNED NULL,
    auteur_id BIGINT UNSIGNED NULL,
    CreatedAt DATETIME NOT NULL,
    UpdatedAt DATETIME NOT NULL,
    PRIMARY KEY (Id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
