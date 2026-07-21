-- Migration Forge
-- Version: 20260721232942
-- Name: indicateur_observe
-- ADR-032 (décision 6) : le professeur coche, dans la feuille, les INDICATEURS
-- qu'il observe pour un critère. Ce pivot mémorise ces coches par observation
-- (evaluation_activite) ; le nombre de coches / total suggère un niveau
-- (suggerer_niveau), que le professeur arbitre. Types réels (BIGINT UNSIGNED).
-- FK observation CASCADE (les coches partent avec l'observation) ; FK indicateur
-- CASCADE (aligné sur le référentiel, comme seance_critere).

CREATE TABLE IF NOT EXISTS indicateur_observe (
    Id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    evaluation_activite_id BIGINT UNSIGNED NOT NULL,
    indicateur_id BIGINT UNSIGNED NOT NULL,
    CreatedAt DATETIME NOT NULL,
    UpdatedAt DATETIME NOT NULL,
    PRIMARY KEY (Id),
    UNIQUE KEY uq_indicateur_observe (evaluation_activite_id, indicateur_id),
    INDEX idx_indicateur_observe_evaluation_activite_id (evaluation_activite_id),
    INDEX idx_indicateur_observe_indicateur_id (indicateur_id),
    CONSTRAINT fk_indicateur_observe_evaluation_activite_id
        FOREIGN KEY (evaluation_activite_id) REFERENCES evaluation_activite (Id) ON DELETE CASCADE,
    CONSTRAINT fk_indicateur_observe_indicateur_id
        FOREIGN KEY (indicateur_id) REFERENCES indicateur_reussite (Id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
