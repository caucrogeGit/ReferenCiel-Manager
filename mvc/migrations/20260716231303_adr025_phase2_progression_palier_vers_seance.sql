-- Migration Forge
-- Version: 20260716231303
-- Name: adr025_phase2_progression_palier_vers_seance
-- ADR-025 phase 2 : ProgressionPalier -> ProgressionSeance. Table
-- progression_palier -> progression_seance ; ses 2 FK sortantes sont
-- renommées ; les dépendants depot_eleve, evaluation_activite, item_coche et
-- tentative_qcm voient leur FK progression_palier_id -> progression_seance_id.
-- Les FK entrantes gardent leur ON DELETE CASCADE ACTUEL (posé par les
-- migrations de création) : un renommage ne change pas la sémantique. La
-- divergence contrat (restrict) / base (cascade) est traitée à part.

RENAME TABLE progression_palier TO progression_seance;

-- FK sortantes de la table renommée (noms de contrainte suivent la table).
ALTER TABLE progression_seance DROP FOREIGN KEY IF EXISTS fk_progression_palier_progression_parcours_id;
ALTER TABLE progression_seance DROP INDEX IF EXISTS fk_progression_palier_progression_parcours_id;
ALTER TABLE progression_seance
    ADD CONSTRAINT fk_progression_seance_progression_parcours_id
        FOREIGN KEY (progression_parcours_id) REFERENCES progression_parcours (Id)
        ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE progression_seance DROP FOREIGN KEY IF EXISTS fk_progression_palier_seance_id;
ALTER TABLE progression_seance DROP INDEX IF EXISTS fk_progression_palier_seance_id;
ALTER TABLE progression_seance
    ADD CONSTRAINT fk_progression_seance_seance_id
        FOREIGN KEY (seance_id) REFERENCES seance (Id)
        ON DELETE RESTRICT ON UPDATE RESTRICT;

-- DepotEleve -> ProgressionSeance
ALTER TABLE depot_eleve DROP FOREIGN KEY IF EXISTS fk_depot_eleve_progression_palier_id;
ALTER TABLE depot_eleve DROP INDEX IF EXISTS fk_depot_eleve_progression_palier_id;
ALTER TABLE depot_eleve CHANGE COLUMN progression_palier_id progression_seance_id BIGINT UNSIGNED NOT NULL;
ALTER TABLE depot_eleve
    ADD CONSTRAINT fk_depot_eleve_progression_seance_id
        FOREIGN KEY (progression_seance_id) REFERENCES progression_seance (Id)
        ON DELETE CASCADE ON UPDATE RESTRICT;

-- EvaluationActivite -> ProgressionSeance
ALTER TABLE evaluation_activite DROP FOREIGN KEY IF EXISTS fk_evaluation_activite_progression_palier_id;
ALTER TABLE evaluation_activite DROP INDEX IF EXISTS fk_evaluation_activite_progression_palier_id;
ALTER TABLE evaluation_activite CHANGE COLUMN progression_palier_id progression_seance_id BIGINT UNSIGNED NOT NULL;
ALTER TABLE evaluation_activite
    ADD CONSTRAINT fk_evaluation_activite_progression_seance_id
        FOREIGN KEY (progression_seance_id) REFERENCES progression_seance (Id)
        ON DELETE CASCADE ON UPDATE RESTRICT;

-- ItemCoche -> ProgressionSeance
ALTER TABLE item_coche DROP FOREIGN KEY IF EXISTS fk_item_coche_progression_palier_id;
ALTER TABLE item_coche DROP INDEX IF EXISTS fk_item_coche_progression_palier_id;
ALTER TABLE item_coche CHANGE COLUMN progression_palier_id progression_seance_id BIGINT UNSIGNED NOT NULL;
ALTER TABLE item_coche
    ADD CONSTRAINT fk_item_coche_progression_seance_id
        FOREIGN KEY (progression_seance_id) REFERENCES progression_seance (Id)
        ON DELETE CASCADE ON UPDATE RESTRICT;

-- TentativeQCM -> ProgressionSeance
ALTER TABLE tentative_qcm DROP FOREIGN KEY IF EXISTS fk_tentative_qcm_progression_palier_id;
ALTER TABLE tentative_qcm DROP INDEX IF EXISTS fk_tentative_qcm_progression_palier_id;
ALTER TABLE tentative_qcm CHANGE COLUMN progression_palier_id progression_seance_id BIGINT UNSIGNED NOT NULL;
ALTER TABLE tentative_qcm
    ADD CONSTRAINT fk_tentative_qcm_progression_seance_id
        FOREIGN KEY (progression_seance_id) REFERENCES progression_seance (Id)
        ON DELETE CASCADE ON UPDATE RESTRICT;
