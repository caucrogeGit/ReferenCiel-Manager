-- Migration Forge
-- Version: 20260721230126
-- Name: remap_niveau_ciel
-- ADR-032 (amendement, Accepté) : la feuille de positionnement adopte la grille
-- officielle CIEL (mvc/services/niveaux_maitrise). Les niveaux hérités
-- (échelle « non_atteint … depasse », antérieurs à l'amendement) sont remappés
-- 1:1 vers les codes CIEL persistés dans evaluation_critere.Niveau, afin que la
-- table ne mélange pas deux vocabulaires et que le bilan agrège correctement.

UPDATE evaluation_critere SET Niveau = 'NIVEAU_1' WHERE Niveau = 'non_atteint';
UPDATE evaluation_critere SET Niveau = 'NIVEAU_2' WHERE Niveau = 'partiellement_atteint';
UPDATE evaluation_critere SET Niveau = 'NIVEAU_3' WHERE Niveau = 'atteint';
UPDATE evaluation_critere SET Niveau = 'NIVEAU_4' WHERE Niveau = 'depasse';
