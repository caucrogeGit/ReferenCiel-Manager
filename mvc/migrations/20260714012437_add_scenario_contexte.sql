-- Migration Forge
-- Version: 20260714012437
-- Name: add_scenario_contexte
-- Section Contexte du scenario (ADR-019, cpro) : cinq champs qui supersedent
-- intention/objectifs (ces derniers restent le temps que le CRUD plat soit
-- retire). Tous optionnels : le contexte se remplit progressivement.

ALTER TABLE scenario
    ADD COLUMN DescriptionContexte TEXT NULL AFTER Objectifs,
    ADD COLUMN Problematique TEXT NULL AFTER DescriptionContexte,
    ADD COLUMN MaterielsLogiciels TEXT NULL AFTER Problematique,
    ADD COLUMN LiensAssocies TEXT NULL AFTER MaterielsLogiciels,
    ADD COLUMN EspacesFormation TEXT NULL AFTER LiensAssocies;
