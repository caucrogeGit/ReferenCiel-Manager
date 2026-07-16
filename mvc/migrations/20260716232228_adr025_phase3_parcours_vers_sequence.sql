-- Migration Forge
-- Version: 20260716232228
-- Name: adr025_phase3_parcours_vers_sequence
-- ADR-025 phase 3 : Parcours -> Sequence (sémantique Éducation nationale, un
-- parcours se nomme séquence). Table parcours -> sequence ; les dépendants
-- seance, progression_parcours et les pivots scenario_parcours /
-- professeur_parcours voient leur FK parcours_id -> sequence_id (les TABLES
-- progression_parcours et pivots sont renommées en phases 4 et 5). Deux noms
-- legacy assainis au passage (uq_palier_parcours_ordre,
-- fk_progression_eleve_parcours_id). Les pivots gardent leur ON DELETE CASCADE.

RENAME TABLE parcours TO sequence;

-- Table renommée : FK sortante + unique d'identifiant renommés.
ALTER TABLE sequence DROP FOREIGN KEY IF EXISTS fk_parcours_niveau_classe_id;
ALTER TABLE sequence DROP INDEX IF EXISTS fk_parcours_niveau_classe_id;
ALTER TABLE sequence
    ADD CONSTRAINT fk_sequence_niveau_classe_id
        FOREIGN KEY (niveau_classe_id) REFERENCES niveau_classe (Id)
        ON DELETE RESTRICT ON UPDATE RESTRICT;
ALTER TABLE sequence ADD UNIQUE INDEX IF NOT EXISTS uq_sequence_identifiant (Identifiant);
ALTER TABLE sequence DROP INDEX IF EXISTS uq_parcours_identifiant;

-- Seance -> Sequence (l'unique composite legacy sert de tête de FK ; renommé).
ALTER TABLE seance DROP FOREIGN KEY IF EXISTS fk_seance_parcours_id;
ALTER TABLE seance CHANGE COLUMN parcours_id sequence_id BIGINT UNSIGNED NOT NULL;
ALTER TABLE seance ADD UNIQUE INDEX IF NOT EXISTS uq_seance_sequence_ordre (sequence_id, Ordre);
ALTER TABLE seance DROP INDEX IF EXISTS uq_palier_parcours_ordre;
ALTER TABLE seance
    ADD CONSTRAINT fk_seance_sequence_id
        FOREIGN KEY (sequence_id) REFERENCES sequence (Id)
        ON DELETE RESTRICT ON UPDATE RESTRICT;

-- ProgressionParcours -> Sequence (contrainte/index legacy progression_eleve).
ALTER TABLE progression_parcours DROP FOREIGN KEY IF EXISTS fk_progression_eleve_parcours_id;
ALTER TABLE progression_parcours DROP INDEX IF EXISTS fk_progression_eleve_parcours_id;
ALTER TABLE progression_parcours CHANGE COLUMN parcours_id sequence_id BIGINT UNSIGNED NOT NULL;
ALTER TABLE progression_parcours
    ADD CONSTRAINT fk_progression_parcours_sequence_id
        FOREIGN KEY (sequence_id) REFERENCES sequence (Id)
        ON DELETE RESTRICT ON UPDATE RESTRICT;

-- Pivot scenario_parcours (table renommée en phase 5). L'unique mono-colonne
-- (1-1 côté séquence) est conservé tel quel dans sa sémantique, renommé.
ALTER TABLE scenario_parcours DROP FOREIGN KEY IF EXISTS fk_scenario_parcours_parcours_id;
ALTER TABLE scenario_parcours CHANGE COLUMN parcours_id sequence_id BIGINT UNSIGNED NOT NULL;
ALTER TABLE scenario_parcours ADD UNIQUE INDEX IF NOT EXISTS uq_scenario_parcours_sequence (sequence_id);
ALTER TABLE scenario_parcours DROP INDEX IF EXISTS uq_scenario_parcours_parcours;
ALTER TABLE scenario_parcours
    ADD CONSTRAINT fk_scenario_parcours_sequence_id
        FOREIGN KEY (sequence_id) REFERENCES sequence (Id)
        ON DELETE CASCADE ON UPDATE RESTRICT;

-- Pivot professeur_parcours (table renommée en phase 5).
ALTER TABLE professeur_parcours DROP FOREIGN KEY IF EXISTS fk_professeur_parcours_parcours_id;
ALTER TABLE professeur_parcours CHANGE COLUMN parcours_id sequence_id BIGINT UNSIGNED NOT NULL;
ALTER TABLE professeur_parcours ADD INDEX IF NOT EXISTS idx_professeur_parcours_sequence_id (sequence_id);
ALTER TABLE professeur_parcours DROP INDEX IF EXISTS idx_professeur_parcours_parcours_id;
ALTER TABLE professeur_parcours
    ADD CONSTRAINT fk_professeur_parcours_sequence_id
        FOREIGN KEY (sequence_id) REFERENCES sequence (Id)
        ON DELETE CASCADE ON UPDATE RESTRICT;
