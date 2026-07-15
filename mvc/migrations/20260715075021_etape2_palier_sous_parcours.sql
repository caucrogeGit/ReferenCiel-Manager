-- Migration Forge
-- Version: 20260715075021
-- Name: etape2_palier_sous_parcours
-- ADR-022 etape 2 : le palier est rattache directement au Parcours
-- (palier n-1 parcours) au lieu de la VersionParcours. On transforme aussi
-- l'unicite metier « ordre unique par version » en « ordre unique par
-- parcours » (uq_palier_version_ordre -> uq_palier_parcours_ordre, cet index
-- vit dans les migrations, cf. create_parcours). Table vide (bloc_b purge).
-- Statements separes + IF [NOT] EXISTS (MariaDB) : idempotent malgre le DDL
-- non transactionnel.

ALTER TABLE palier
    ADD COLUMN IF NOT EXISTS parcours_id BIGINT UNSIGNED NOT NULL AFTER DossierTechniqueFichier;

ALTER TABLE palier DROP FOREIGN KEY IF EXISTS fk_palier_version_parcours_id;
ALTER TABLE palier DROP INDEX IF EXISTS uq_palier_version_ordre;
ALTER TABLE palier DROP INDEX IF EXISTS fk_palier_version_parcours_id;
ALTER TABLE palier DROP COLUMN IF EXISTS version_parcours_id;

ALTER TABLE palier DROP INDEX IF EXISTS uq_palier_parcours_ordre;
ALTER TABLE palier ADD UNIQUE KEY uq_palier_parcours_ordre (parcours_id, Ordre);

ALTER TABLE palier DROP FOREIGN KEY IF EXISTS fk_palier_parcours_id;
ALTER TABLE palier
    ADD CONSTRAINT fk_palier_parcours_id
        FOREIGN KEY (parcours_id)
        REFERENCES parcours (Id)
        ON DELETE RESTRICT
        ON UPDATE RESTRICT;
