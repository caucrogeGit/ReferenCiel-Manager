-- Migration Forge
-- Version: 20260715090233
-- Name: etape6b_rename_progression_parcours
-- ADR-022 etape 6b : renommage ProgressionEleve -> ProgressionParcours
-- (table progression_eleve -> progression_parcours). Les dependants
-- ProgressionPalier et BilanEleve voient leur FK progression_eleve_id ->
-- progression_parcours_id. Tables vides.

RENAME TABLE progression_eleve TO progression_parcours;

-- ProgressionPalier -> ProgressionParcours
ALTER TABLE progression_palier DROP FOREIGN KEY IF EXISTS fk_progression_palier_progression_eleve_id;
ALTER TABLE progression_palier DROP INDEX IF EXISTS fk_progression_palier_progression_eleve_id;
ALTER TABLE progression_palier CHANGE COLUMN progression_eleve_id progression_parcours_id BIGINT UNSIGNED NOT NULL;
ALTER TABLE progression_palier
    ADD CONSTRAINT fk_progression_palier_progression_parcours_id
        FOREIGN KEY (progression_parcours_id) REFERENCES progression_parcours (Id)
        ON DELETE RESTRICT ON UPDATE RESTRICT;

-- BilanEleve -> ProgressionParcours
ALTER TABLE bilan_eleve DROP FOREIGN KEY IF EXISTS fk_bilan_eleve_progression_eleve_id;
ALTER TABLE bilan_eleve DROP INDEX IF EXISTS fk_bilan_eleve_progression_eleve_id;
ALTER TABLE bilan_eleve CHANGE COLUMN progression_eleve_id progression_parcours_id BIGINT UNSIGNED NOT NULL;
ALTER TABLE bilan_eleve
    ADD CONSTRAINT fk_bilan_eleve_progression_parcours_id
        FOREIGN KEY (progression_parcours_id) REFERENCES progression_parcours (Id)
        ON DELETE RESTRICT ON UPDATE RESTRICT;
