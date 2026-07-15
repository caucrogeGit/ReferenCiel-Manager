-- Migration Forge
-- Version: 20260715191057
-- Name: adr023_p1a_formation_type
-- ADR-023 phase 1a : une Formation porte un type (FAMILLE_METIERS,
-- SPECIALITE_BAC_PRO, CAP, BP, BMA, CERTIFICAT_SPECIALISATION, FCIL, BTS, AUTRE).
-- On ajoute la colonne nullable, on backfille, puis on la rend obligatoire.
-- Idempotent (IF [NOT] EXISTS).

-- 1) Nouvelle colonne, nullable le temps du backfill.
ALTER TABLE formation ADD COLUMN IF NOT EXISTS Type VARCHAR(40) NULL AFTER Code;

-- 2) Backfill : CIEL est une spécialité de bac pro ; le reste par défaut AUTRE.
UPDATE formation SET Type = 'SPECIALITE_BAC_PRO' WHERE Code = 'BACPRO-CIEL' AND Type IS NULL;
UPDATE formation SET Type = 'AUTRE' WHERE Type IS NULL;

-- 3) Type devient obligatoire.
ALTER TABLE formation MODIFY COLUMN Type VARCHAR(40) NOT NULL;
