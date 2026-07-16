-- Migration Forge
-- Version: 20260716232921
-- Name: adr025_phase4_progression_parcours_vers_sequence
-- ADR-025 phase 4 : ProgressionParcours -> ProgressionSequence. Table
-- progression_parcours -> progression_sequence ; ses FK sortantes (eleve,
-- sequence) et l'unique composite prennent les noms de la nouvelle table (les
-- noms legacy progression_eleve sont assainis) ; les dépendants
-- progression_seance et bilan_eleve voient leur FK
-- progression_parcours_id -> progression_sequence_id.

RENAME TABLE progression_parcours TO progression_sequence;

-- FK sortantes (noms legacy progression_eleve / progression_parcours).
ALTER TABLE progression_sequence DROP FOREIGN KEY IF EXISTS fk_progression_eleve_eleve_id;
ALTER TABLE progression_sequence DROP INDEX IF EXISTS fk_progression_eleve_eleve_id;
ALTER TABLE progression_sequence
    ADD CONSTRAINT fk_progression_sequence_eleve_id
        FOREIGN KEY (eleve_id) REFERENCES eleve (Id)
        ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE progression_sequence DROP FOREIGN KEY IF EXISTS fk_progression_parcours_sequence_id;
ALTER TABLE progression_sequence DROP INDEX IF EXISTS fk_progression_parcours_sequence_id;
ALTER TABLE progression_sequence
    ADD CONSTRAINT fk_progression_sequence_sequence_id
        FOREIGN KEY (sequence_id) REFERENCES sequence (Id)
        ON DELETE RESTRICT ON UPDATE RESTRICT;

-- Unique composite legacy (tête de FK eleve) : renommé.
ALTER TABLE progression_sequence ADD UNIQUE INDEX IF NOT EXISTS uq_progression_sequence_eleve_sequence (eleve_id, sequence_id);
ALTER TABLE progression_sequence DROP INDEX IF EXISTS uq_progression_eleve_eleve_parcours;

-- ProgressionSeance -> ProgressionSequence
ALTER TABLE progression_seance DROP FOREIGN KEY IF EXISTS fk_progression_seance_progression_parcours_id;
ALTER TABLE progression_seance DROP INDEX IF EXISTS fk_progression_seance_progression_parcours_id;
ALTER TABLE progression_seance CHANGE COLUMN progression_parcours_id progression_sequence_id BIGINT UNSIGNED NOT NULL;
ALTER TABLE progression_seance
    ADD CONSTRAINT fk_progression_seance_progression_sequence_id
        FOREIGN KEY (progression_sequence_id) REFERENCES progression_sequence (Id)
        ON DELETE RESTRICT ON UPDATE RESTRICT;

-- BilanEleve -> ProgressionSequence
ALTER TABLE bilan_eleve DROP FOREIGN KEY IF EXISTS fk_bilan_eleve_progression_parcours_id;
ALTER TABLE bilan_eleve DROP INDEX IF EXISTS fk_bilan_eleve_progression_parcours_id;
ALTER TABLE bilan_eleve CHANGE COLUMN progression_parcours_id progression_sequence_id BIGINT UNSIGNED NOT NULL;
ALTER TABLE bilan_eleve
    ADD CONSTRAINT fk_bilan_eleve_progression_sequence_id
        FOREIGN KEY (progression_sequence_id) REFERENCES progression_sequence (Id)
        ON DELETE RESTRICT ON UPDATE RESTRICT;
