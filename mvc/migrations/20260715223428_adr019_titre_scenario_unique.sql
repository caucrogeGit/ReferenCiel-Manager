-- Migration Forge
-- Version: 20260715223428
-- Name: adr019_titre_scenario_unique
-- Le titre d'un scenario est unique (ADR-019). Les doublons « Test » ont ete
-- nettoyes au prealable (un seul conserve). Idempotent (IF NOT EXISTS).

CREATE UNIQUE INDEX IF NOT EXISTS uk_scenario_titre ON scenario (Titre);
