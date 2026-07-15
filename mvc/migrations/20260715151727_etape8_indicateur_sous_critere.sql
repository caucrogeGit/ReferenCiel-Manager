-- Migration Forge
-- Version: 20260715151727
-- Name: etape8_indicateur_sous_critere
-- Un indicateur de réussite n'existe que rattaché à un CRITERE (Critère 1 - 0..n
-- Indicateur, option A). On retire l'origine polymorphe et le rattachement au
-- référentiel (déduit via critère -> compétence -> référentiel).
--   - seuls les indicateurs d'origine 'critere' survivent (les autres = amorces
--     sans critère, supprimées) ;
--   - critere_id est backfillé depuis RefCode (= code canonique du critère =
--     critere_observable.Code), scopé au référentiel.

-- 1) Ne garder que les indicateurs rattachés à un critère.
DELETE FROM indicateur_reussite WHERE Origine <> 'critere';

-- 2) Nouvelle FK, nullable le temps du backfill.
ALTER TABLE indicateur_reussite ADD COLUMN IF NOT EXISTS critere_id BIGINT UNSIGNED NULL AFTER Libelle;

-- 3) Backfill RefCode -> critere_observable.Code (dans le bon référentiel).
UPDATE indicateur_reussite i
    JOIN critere_observable c ON c.Code = i.RefCode
    JOIN competence cp ON cp.Id = c.competence_id AND cp.referentiel_id = i.referentiel_id
    SET i.critere_id = c.Id;

-- 4) critere_id devient obligatoire.
ALTER TABLE indicateur_reussite MODIFY COLUMN critere_id BIGINT UNSIGNED NOT NULL;

-- 5) Retirer l'ancien rattachement (référentiel + provenance polymorphe).
ALTER TABLE indicateur_reussite DROP FOREIGN KEY IF EXISTS fk_indicateur_reussite_referentiel_id;
ALTER TABLE indicateur_reussite DROP INDEX IF EXISTS uq_indicateur_ref_code;
ALTER TABLE indicateur_reussite DROP INDEX IF EXISTS fk_indicateur_reussite_referentiel_id;
ALTER TABLE indicateur_reussite DROP COLUMN IF EXISTS referentiel_id;
ALTER TABLE indicateur_reussite DROP COLUMN IF EXISTS Origine;
ALTER TABLE indicateur_reussite DROP COLUMN IF EXISTS RefCode;

-- 6) FK vers le critère (cascade : un critère supprimé emporte ses indicateurs).
ALTER TABLE indicateur_reussite DROP FOREIGN KEY IF EXISTS fk_indicateur_reussite_critere_id;
ALTER TABLE indicateur_reussite
    ADD CONSTRAINT fk_indicateur_reussite_critere_id
        FOREIGN KEY (critere_id) REFERENCES critere_observable (Id)
        ON DELETE CASCADE ON UPDATE RESTRICT;
