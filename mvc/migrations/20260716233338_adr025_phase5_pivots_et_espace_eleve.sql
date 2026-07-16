-- Migration Forge
-- Version: 20260716233338
-- Name: adr025_phase5_pivots_et_espace_eleve
-- ADR-025 phase 5 : renommage des pivots scenario_parcours -> scenario_sequence
-- et professeur_parcours -> professeur_sequence (les colonnes sequence_id ont
-- déjà été renommées en phase 3). Contraintes, uniques et index prennent les
-- noms de la nouvelle table ; ON DELETE CASCADE conservé. La sémantique 1-1 du
-- pivot scénario (uniques mono-colonnes) est conservée telle quelle.

RENAME TABLE scenario_parcours TO scenario_sequence;

ALTER TABLE scenario_sequence DROP FOREIGN KEY IF EXISTS fk_scenario_parcours_scenario_id;
ALTER TABLE scenario_sequence DROP FOREIGN KEY IF EXISTS fk_scenario_parcours_sequence_id;
ALTER TABLE scenario_sequence ADD UNIQUE INDEX IF NOT EXISTS uq_scenario_sequence_scenario (scenario_id);
ALTER TABLE scenario_sequence ADD UNIQUE INDEX IF NOT EXISTS uq_scenario_sequence_sequence (sequence_id);
ALTER TABLE scenario_sequence DROP INDEX IF EXISTS uq_scenario_parcours_scenario;
ALTER TABLE scenario_sequence DROP INDEX IF EXISTS uq_scenario_parcours_sequence;
ALTER TABLE scenario_sequence
    ADD CONSTRAINT fk_scenario_sequence_scenario_id
        FOREIGN KEY (scenario_id) REFERENCES scenario (Id)
        ON DELETE CASCADE ON UPDATE RESTRICT;
ALTER TABLE scenario_sequence
    ADD CONSTRAINT fk_scenario_sequence_sequence_id
        FOREIGN KEY (sequence_id) REFERENCES sequence (Id)
        ON DELETE CASCADE ON UPDATE RESTRICT;

RENAME TABLE professeur_parcours TO professeur_sequence;

ALTER TABLE professeur_sequence DROP FOREIGN KEY IF EXISTS fk_professeur_parcours_professeur_id;
ALTER TABLE professeur_sequence DROP FOREIGN KEY IF EXISTS fk_professeur_parcours_sequence_id;
ALTER TABLE professeur_sequence ADD UNIQUE INDEX IF NOT EXISTS uq_professeur_sequence (professeur_id, sequence_id);
ALTER TABLE professeur_sequence ADD INDEX IF NOT EXISTS idx_professeur_sequence_professeur_id (professeur_id);
ALTER TABLE professeur_sequence ADD INDEX IF NOT EXISTS idx_professeur_sequence_sequence_id (sequence_id);
ALTER TABLE professeur_sequence DROP INDEX IF EXISTS uq_professeur_parcours;
ALTER TABLE professeur_sequence DROP INDEX IF EXISTS idx_professeur_parcours_professeur_id;
ALTER TABLE professeur_sequence DROP INDEX IF EXISTS idx_professeur_parcours_sequence_id;
ALTER TABLE professeur_sequence
    ADD CONSTRAINT fk_professeur_sequence_professeur_id
        FOREIGN KEY (professeur_id) REFERENCES professeur (Id)
        ON DELETE CASCADE ON UPDATE RESTRICT;
ALTER TABLE professeur_sequence
    ADD CONSTRAINT fk_professeur_sequence_sequence_id
        FOREIGN KEY (sequence_id) REFERENCES sequence (Id)
        ON DELETE CASCADE ON UPDATE RESTRICT;
