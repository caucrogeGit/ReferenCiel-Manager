-- Migration Forge
-- Version: 20260715082613
-- Name: etape4_dossier_technique_et_ressources
-- ADR-022 etape 4 : le dossier technique devient un conteneur.
--   - DossierTechnique (1-1 palier) remplace le champ palier.DossierTechniqueFichier
--   - RessourceDossier (1-n) : ressources typees markdown/video/audio/lien
--   - QCM de validation repointe du Palier vers le DossierTechnique (1-1)
-- Tables pedagogiques vides ; idempotent (IF [NOT] EXISTS).

CREATE TABLE IF NOT EXISTS dossier_technique (
    Id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    Titre VARCHAR(200) NOT NULL,
    palier_id BIGINT UNSIGNED NOT NULL,
    CreatedAt DATETIME NOT NULL,
    UpdatedAt DATETIME NOT NULL,
    PRIMARY KEY (Id),
    UNIQUE KEY uq_dossier_technique_palier (palier_id),
    CONSTRAINT fk_dossier_technique_palier_id
        FOREIGN KEY (palier_id) REFERENCES palier (Id)
        ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS ressource_dossier (
    Id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    Type VARCHAR(20) NOT NULL,
    Titre VARCHAR(200) NOT NULL,
    Ordre INT NOT NULL,
    Contenu TEXT NULL,
    MediaRef VARCHAR(255) NULL,
    Url VARCHAR(500) NULL,
    dossier_technique_id BIGINT UNSIGNED NOT NULL,
    CreatedAt DATETIME NOT NULL,
    UpdatedAt DATETIME NOT NULL,
    PRIMARY KEY (Id),
    KEY idx_ressource_dossier_dossier_technique_id (dossier_technique_id),
    CONSTRAINT fk_ressource_dossier_dossier_technique_id
        FOREIGN KEY (dossier_technique_id) REFERENCES dossier_technique (Id)
        ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Palier : le fichier unique laisse place au conteneur DossierTechnique.
ALTER TABLE palier DROP COLUMN IF EXISTS DossierTechniqueFichier;

-- QCM de validation : rattache au dossier technique (1-1) au lieu du palier.
ALTER TABLE qcm ADD COLUMN IF NOT EXISTS dossier_technique_id BIGINT UNSIGNED NOT NULL AFTER palier_id;
ALTER TABLE qcm DROP FOREIGN KEY IF EXISTS fk_qcm_palier_id;
ALTER TABLE qcm DROP INDEX IF EXISTS uq_qcm_palier;
ALTER TABLE qcm DROP INDEX IF EXISTS fk_qcm_palier_id;
ALTER TABLE qcm DROP COLUMN IF EXISTS palier_id;
ALTER TABLE qcm DROP INDEX IF EXISTS uq_qcm_dossier;
ALTER TABLE qcm ADD UNIQUE KEY uq_qcm_dossier (dossier_technique_id);
ALTER TABLE qcm DROP FOREIGN KEY IF EXISTS fk_qcm_dossier_technique_id;
ALTER TABLE qcm
    ADD CONSTRAINT fk_qcm_dossier_technique_id
        FOREIGN KEY (dossier_technique_id) REFERENCES dossier_technique (Id)
        ON DELETE RESTRICT ON UPDATE RESTRICT;
