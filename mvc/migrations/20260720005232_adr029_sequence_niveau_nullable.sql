-- Migration Forge
-- Version: 20260720005232
-- Name: adr029_sequence_niveau_nullable
-- ADR-029 : une séquence peut naître appairée à un scénario avant que son niveau
-- de classe ne soit renseigné (rempli ensuite dans le tunnel). niveau_classe_id
-- passe donc de NOT NULL à nullable. La FK (ON DELETE RESTRICT) est conservée.

ALTER TABLE sequence MODIFY niveau_classe_id BIGINT UNSIGNED NULL;
