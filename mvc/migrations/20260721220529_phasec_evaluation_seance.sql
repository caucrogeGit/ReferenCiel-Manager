-- Migration Forge
-- Version: 20260721220529
-- Name: phasec_evaluation_seance
-- ADR-032 phase C : alignement du moteur d'évaluation sur la séance/élément.
--   evaluation_activite : l'observation référence l'élément de séance observé,
--     la production/preuve et l'aide apportée ; activite_id devient facultatif
--     (le modèle est centré séance, l'activité est optionnelle/héritée).
--   evaluation_critere : le critère observé référence l'indicateur utilisé.
-- Colonnes additives et nullables ; FK SET NULL (l'observation survit si l'objet
-- référencé disparaît). Le CRUD existant continue de fonctionner (défauts NULL).

ALTER TABLE evaluation_activite
    ADD COLUMN IF NOT EXISTS Production TEXT NULL AFTER Appreciation,
    ADD COLUMN IF NOT EXISTS AideApportee TEXT NULL AFTER Production,
    ADD COLUMN IF NOT EXISTS element_seance_id BIGINT UNSIGNED NULL AFTER activite_id,
    MODIFY activite_id BIGINT UNSIGNED NULL;

ALTER TABLE evaluation_activite
    ADD INDEX idx_evaluation_activite_element_seance_id (element_seance_id),
    ADD CONSTRAINT fk_evaluation_activite_element_seance_id
        FOREIGN KEY (element_seance_id) REFERENCES element_seance (Id) ON DELETE SET NULL;

ALTER TABLE evaluation_critere
    ADD COLUMN IF NOT EXISTS indicateur_id BIGINT UNSIGNED NULL AFTER critere_id;

ALTER TABLE evaluation_critere
    ADD INDEX idx_evaluation_critere_indicateur_id (indicateur_id),
    ADD CONSTRAINT fk_evaluation_critere_indicateur_id
        FOREIGN KEY (indicateur_id) REFERENCES indicateur_reussite (Id) ON DELETE SET NULL;
