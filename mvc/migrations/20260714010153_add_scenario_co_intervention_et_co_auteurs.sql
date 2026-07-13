-- Migration Forge
-- Version: 20260714010153
-- Name: add_scenario_co_intervention_et_co_auteurs
-- Section Titre du scenario (ADR-019) : indicateur de co-intervention et
-- co-auteurs (m2m scenario <-> professeur). Le pivot est cree en
-- BIGINT UNSIGNED pour matcher scenario.Id et professeur.Id ; le INT emis
-- par sync:relations ferait echouer les FK (cf. retour-013).

ALTER TABLE scenario ADD COLUMN CoIntervention BOOLEAN NOT NULL DEFAULT 0 AFTER Version;

CREATE TABLE scenario_professeur (
    Id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    scenario_id BIGINT UNSIGNED NOT NULL,
    professeur_id BIGINT UNSIGNED NOT NULL,
    PRIMARY KEY (Id),
    UNIQUE KEY uq_scenario_professeur (scenario_id, professeur_id),
    KEY idx_scenario_professeur_scenario_id (scenario_id),
    KEY idx_scenario_professeur_professeur_id (professeur_id),
    CONSTRAINT fk_scenario_professeur_scenario_id FOREIGN KEY (scenario_id) REFERENCES scenario (Id) ON DELETE CASCADE,
    CONSTRAINT fk_scenario_professeur_professeur_id FOREIGN KEY (professeur_id) REFERENCES professeur (Id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
