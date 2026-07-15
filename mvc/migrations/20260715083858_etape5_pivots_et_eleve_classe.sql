-- Migration Forge
-- Version: 20260715083858
-- Name: etape5_pivots_et_eleve_classe
-- ADR-022 etape 5 : liens n-n et rattachement direct de l'eleve a la classe.
--   - eleve.niveau_classe_id -> eleve.classe_id (eleve n-1 classe ;
--     le niveau se deduit de classe.niveau_classe_id)
--   - scenario_parcours : pivot 1-1 (unique sur CHAQUE colonne) pour naviguer
--     scenario <-> parcours dans les deux sens, l'un pouvant exister sans l'autre
--   - classe_professeur : pivot n-n (remplace affectation_professeur_classe,
--     l'annee se deduit de la classe)
--   - professeur_parcours : pivot n-n (propriete/co-conception)
-- Demo structure videe au prealable ; idempotent (IF [NOT] EXISTS).

-- Eleve : rattachement direct a la classe.
ALTER TABLE eleve ADD COLUMN IF NOT EXISTS classe_id BIGINT UNSIGNED NOT NULL AFTER niveau_classe_id;
ALTER TABLE eleve DROP FOREIGN KEY IF EXISTS fk_eleve_niveau_classe_id;
ALTER TABLE eleve DROP INDEX IF EXISTS fk_eleve_niveau_classe_id;
ALTER TABLE eleve DROP COLUMN IF EXISTS niveau_classe_id;
ALTER TABLE eleve DROP FOREIGN KEY IF EXISTS fk_eleve_classe_id;
ALTER TABLE eleve
    ADD CONSTRAINT fk_eleve_classe_id
        FOREIGN KEY (classe_id) REFERENCES classe (Id)
        ON DELETE RESTRICT ON UPDATE RESTRICT;

-- Scenario <-> Parcours : 1-1 par pivot a id technique (unique par colonne).
CREATE TABLE IF NOT EXISTS scenario_parcours (
    Id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    scenario_id BIGINT UNSIGNED NOT NULL,
    parcours_id BIGINT UNSIGNED NOT NULL,
    PRIMARY KEY (Id),
    UNIQUE KEY uq_scenario_parcours_scenario (scenario_id),
    UNIQUE KEY uq_scenario_parcours_parcours (parcours_id),
    CONSTRAINT fk_scenario_parcours_scenario_id FOREIGN KEY (scenario_id) REFERENCES scenario (Id) ON DELETE CASCADE,
    CONSTRAINT fk_scenario_parcours_parcours_id FOREIGN KEY (parcours_id) REFERENCES parcours (Id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Classe <-> Professeur : n-n.
CREATE TABLE IF NOT EXISTS classe_professeur (
    Id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    classe_id BIGINT UNSIGNED NOT NULL,
    professeur_id BIGINT UNSIGNED NOT NULL,
    PRIMARY KEY (Id),
    UNIQUE KEY uq_classe_professeur (classe_id, professeur_id),
    KEY idx_classe_professeur_classe_id (classe_id),
    KEY idx_classe_professeur_professeur_id (professeur_id),
    CONSTRAINT fk_classe_professeur_classe_id FOREIGN KEY (classe_id) REFERENCES classe (Id) ON DELETE CASCADE,
    CONSTRAINT fk_classe_professeur_professeur_id FOREIGN KEY (professeur_id) REFERENCES professeur (Id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Professeur <-> Parcours : n-n.
CREATE TABLE IF NOT EXISTS professeur_parcours (
    Id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    professeur_id BIGINT UNSIGNED NOT NULL,
    parcours_id BIGINT UNSIGNED NOT NULL,
    PRIMARY KEY (Id),
    UNIQUE KEY uq_professeur_parcours (professeur_id, parcours_id),
    KEY idx_professeur_parcours_professeur_id (professeur_id),
    KEY idx_professeur_parcours_parcours_id (parcours_id),
    CONSTRAINT fk_professeur_parcours_professeur_id FOREIGN KEY (professeur_id) REFERENCES professeur (Id) ON DELETE CASCADE,
    CONSTRAINT fk_professeur_parcours_parcours_id FOREIGN KEY (parcours_id) REFERENCES parcours (Id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
