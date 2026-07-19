CREATE TABLE IF NOT EXISTS seance (
    Id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    Ordre INT NOT NULL,
    Titre VARCHAR(200) NOT NULL,
    Theme VARCHAR(100) NULL,
    ProductionAttendue VARCHAR(255) NULL,
    ObjectifOperationnel TEXT NULL,
    ConsigneGenerale TEXT NULL,
    DureeEstimeeMinutes INT NULL,
    ModalitePedagogique VARCHAR(100) NULL,
    ConditionRealisation TEXT NULL,
    ConditionValidation TEXT NULL,
    Remediation TEXT NULL,
    sequence_id BIGINT UNSIGNED NOT NULL,
    CreatedAt DATETIME NOT NULL,
    UpdatedAt DATETIME NOT NULL,
    PRIMARY KEY (Id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
