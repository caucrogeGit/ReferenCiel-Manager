-- Migration Forge
-- Version: 20260723142536
-- Name: sequence_nature
-- Nature de la séquence (ADR-036) : formative (défaut) ou certificative (CCF).
-- Contextualise les statuts attendus des savoirs et les signaux de cohérence ;
-- fournira ses jalons certificatifs au futur plan de formation.

ALTER TABLE sequence ADD COLUMN Nature VARCHAR(20) NOT NULL DEFAULT 'formative' AFTER OrdreImpose;
