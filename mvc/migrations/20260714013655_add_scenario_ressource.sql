-- Migration Forge
-- Version: 20260714013655
-- Name: add_scenario_ressource
-- Section Ressources du scenario (ADR-019, cpro) : metadonnees des fichiers
-- deposes pour un scenario. Les fichiers eux-memes sont stockes par l'opt-in
-- forge-mvc-files (save_upload, category scenarios/<id>) ; on garde ici le nom
-- d'origine, le chemin media (pour /media), le type et la taille.

CREATE TABLE scenario_ressource (
    Id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    scenario_id BIGINT UNSIGNED NOT NULL,
    NomOriginal VARCHAR(255) NOT NULL,
    CheminMedia VARCHAR(500) NOT NULL,
    MimeType VARCHAR(100) NULL,
    Taille BIGINT UNSIGNED NOT NULL DEFAULT 0,
    CreatedAt DATETIME NOT NULL,
    PRIMARY KEY (Id),
    KEY idx_scenario_ressource_scenario_id (scenario_id),
    CONSTRAINT fk_scenario_ressource_scenario_id FOREIGN KEY (scenario_id) REFERENCES scenario (Id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
