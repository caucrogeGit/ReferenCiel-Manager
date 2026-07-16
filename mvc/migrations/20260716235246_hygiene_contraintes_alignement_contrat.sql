-- Migration Forge
-- Version: 20260716235246
-- Name: hygiene_contraintes_alignement_contrat
-- Hygiène : aligne la base sur le contrat pour que installation fraîche
-- (db:init depuis relations.sql) et base migrée soient identiques.
-- 1) Les règles ON DELETE des compositions divergeaient : la base disait
--    CASCADE (posé par les migrations de création), relations.json disait
--    restrict (défaut jamais choisi). Décision : CASCADE au contrat — les
--    contenus de composition (questions/choix, sections/items, réponses,
--    données d'exécution d'une progression) suivent leur parent. La base est
--    déjà en CASCADE : relations.json a été aligné, AUCUN changement de règle
--    ici.
-- 2) Un nom de contrainte legacy restait désaligné sur le pivot
--    scenario_activite : renommage pur (même colonne, même règle CASCADE).

ALTER TABLE scenario_activite DROP FOREIGN KEY IF EXISTS fk_scenario_activite_activite_id;
ALTER TABLE scenario_activite
    ADD CONSTRAINT fk_scenario_activite_activite_professionnelle_id
        FOREIGN KEY (activite_professionnelle_id) REFERENCES activite_professionnelle (Id)
        ON DELETE CASCADE ON UPDATE RESTRICT;
