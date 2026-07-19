-- Migration Forge
-- Version: 20260719215657
-- Name: seq02_colonnes_institutionnelles
-- SEQ-02 : champs institutionnels (vademecum voie pro) sur la séquence et la
-- séance. Frontière A (le « cadre » — contexte, problématique, objectifs,
-- compétences, critères — reste porté par le scénario). Tout est additif et
-- nullable : aucune donnée existante n'est touchée.

ALTER TABLE sequence
    ADD COLUMN IF NOT EXISTS Prerequis TEXT NULL AFTER OrdreImpose,
    ADD COLUMN IF NOT EXISTS PositionnementProgression TEXT NULL AFTER Prerequis,
    ADD COLUMN IF NOT EXISTS DureeEstimee VARCHAR(100) NULL AFTER PositionnementProgression,
    ADD COLUMN IF NOT EXISTS ModalitesEvaluation TEXT NULL AFTER DureeEstimee;

ALTER TABLE seance
    ADD COLUMN IF NOT EXISTS ObjectifOperationnel TEXT NULL AFTER ProductionAttendue,
    ADD COLUMN IF NOT EXISTS ConsigneGenerale TEXT NULL AFTER ObjectifOperationnel,
    ADD COLUMN IF NOT EXISTS DureeEstimeeMinutes INT NULL AFTER ConsigneGenerale,
    ADD COLUMN IF NOT EXISTS ModalitePedagogique VARCHAR(100) NULL AFTER DureeEstimeeMinutes,
    ADD COLUMN IF NOT EXISTS ConditionRealisation TEXT NULL AFTER ModalitePedagogique,
    ADD COLUMN IF NOT EXISTS ConditionValidation TEXT NULL AFTER ConditionRealisation,
    ADD COLUMN IF NOT EXISTS Remediation TEXT NULL AFTER ConditionValidation;
