-- Migration Forge
-- Version: 20260715081456
-- Name: etape3_progression_vers_parcours
-- ADR-022 etape 3 : la progression vise directement le Parcours au lieu de
-- l'affectation (progression n-1 parcours). La progression fusionne ainsi
-- l'affectation : rien ne pointe plus vers affectation_parcours (droppee a
-- l'etape 6). L'unicite « une progression par (eleve, affectation) » devient
-- « une progression par (eleve, parcours) ». (Renommage cosmetique
-- ProgressionEleve -> ProgressionParcours en etape dediee ulterieure.)
-- Table vide (bloc_b purge) ; migration idempotente (IF [NOT] EXISTS).
--
-- ORDRE IMPORTANT : on cree le nouvel unique (eleve_id, parcours_id) AVANT de
-- retirer l'ancien (eleve_id, affectation_parcours_id), car ce dernier fournit
-- l'index de tete du FK eleve_id ; sans le nouveau, MariaDB refuse le drop.

ALTER TABLE progression_eleve
    ADD COLUMN IF NOT EXISTS parcours_id BIGINT UNSIGNED NOT NULL AFTER affectation_parcours_id;

ALTER TABLE progression_eleve DROP INDEX IF EXISTS uq_progression_eleve_eleve_parcours;
ALTER TABLE progression_eleve ADD UNIQUE KEY uq_progression_eleve_eleve_parcours (eleve_id, parcours_id);

ALTER TABLE progression_eleve DROP FOREIGN KEY IF EXISTS fk_progression_eleve_affectation_parcours_id;
ALTER TABLE progression_eleve DROP INDEX IF EXISTS uq_progression_eleve_eleve_affectation;
ALTER TABLE progression_eleve DROP INDEX IF EXISTS fk_progression_eleve_affectation_parcours_id;
ALTER TABLE progression_eleve DROP COLUMN IF EXISTS affectation_parcours_id;

ALTER TABLE progression_eleve DROP FOREIGN KEY IF EXISTS fk_progression_eleve_parcours_id;
ALTER TABLE progression_eleve
    ADD CONSTRAINT fk_progression_eleve_parcours_id
        FOREIGN KEY (parcours_id)
        REFERENCES parcours (Id)
        ON DELETE RESTRICT
        ON UPDATE RESTRICT;
