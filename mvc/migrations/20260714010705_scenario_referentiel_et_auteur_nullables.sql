-- Migration Forge
-- Version: 20260714010705
-- Name: scenario_referentiel_et_auteur_nullables
-- Modele cpro : un scenario se remplit par sections (ADR-019). Le referentiel
-- se choisit en section Liaison, l'auteur quand il est connu ; un scenario nait
-- donc avec juste un titre. On rend referentiel_id et auteur_id nullables.
-- Les cles etrangeres restent (une valeur presente doit pointer une ligne valide).

ALTER TABLE scenario MODIFY referentiel_id BIGINT UNSIGNED NULL;
ALTER TABLE scenario MODIFY auteur_id BIGINT UNSIGNED NULL;
