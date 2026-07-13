-- Migration Forge
-- Version: 20260714012957
-- Name: add_scenario_activite_pivot
-- Section Liaison du scenario (ADR-019, cpro) : le scenario cible des activites
-- professionnelles du referentiel (m2m). Pivot en BIGINT UNSIGNED pour matcher
-- scenario.Id et activite_professionnelle.Id (le INT de sync:relations casserait
-- les FK, cf. retour-013).

CREATE TABLE scenario_activite (
    Id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    scenario_id BIGINT UNSIGNED NOT NULL,
    activite_professionnelle_id BIGINT UNSIGNED NOT NULL,
    PRIMARY KEY (Id),
    UNIQUE KEY uq_scenario_activite (scenario_id, activite_professionnelle_id),
    KEY idx_scenario_activite_scenario_id (scenario_id),
    KEY idx_scenario_activite_activite_id (activite_professionnelle_id),
    CONSTRAINT fk_scenario_activite_scenario_id FOREIGN KEY (scenario_id) REFERENCES scenario (Id) ON DELETE CASCADE,
    CONSTRAINT fk_scenario_activite_activite_id FOREIGN KEY (activite_professionnelle_id) REFERENCES activite_professionnelle (Id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
