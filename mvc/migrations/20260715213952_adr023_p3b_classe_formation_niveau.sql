-- Migration Forge
-- Version: 20260715213952
-- Name: adr023_p3b_classe_formation_niveau
-- ADR-023 phase 3b : la Classe est l'instance locale d'un FormationNiveau
-- (ex. « CIEL/Premiere »), plus d'un niveau de classe nu.
--   - ajout de classe.formation_niveau_id ;
--   - backfill : les classes de niveau SECONDE_PRO -> FormationNiveau 2TNE
--     (la 2nde commune ; seule classe existante « Seconde TNE A ») ;
--   - retrait de classe.niveau_classe_id (FK + index + colonne).
-- Idempotent (IF [NOT] EXISTS, backfill cible).

-- 1) Nouvelle colonne, nullable le temps du backfill.
ALTER TABLE classe ADD COLUMN IF NOT EXISTS formation_niveau_id BIGINT UNSIGNED NULL AFTER niveau_classe_id;

-- 2) Backfill : classe de 2nde pro -> FormationNiveau 2TNE (2nde commune).
UPDATE classe c
    JOIN niveau_classe nc ON nc.Id = c.niveau_classe_id AND nc.Code = 'SECONDE_PRO'
    JOIN formation_niveau fn ON fn.Code = '2TNE'
    SET c.formation_niveau_id = fn.Id
    WHERE c.formation_niveau_id IS NULL;

-- 3) Colonne obligatoire + FK.
ALTER TABLE classe MODIFY COLUMN formation_niveau_id BIGINT UNSIGNED NOT NULL;
ALTER TABLE classe DROP FOREIGN KEY IF EXISTS fk_classe_formation_niveau_id;
ALTER TABLE classe
    ADD CONSTRAINT fk_classe_formation_niveau_id
        FOREIGN KEY (formation_niveau_id) REFERENCES formation_niveau (Id)
        ON DELETE RESTRICT ON UPDATE RESTRICT;

-- 4) Retrait de l'ancien rattachement au niveau de classe.
ALTER TABLE classe DROP FOREIGN KEY IF EXISTS fk_classe_niveau_classe_id;
ALTER TABLE classe DROP INDEX IF EXISTS idx_classe_niveau_classe_id;
ALTER TABLE classe DROP COLUMN IF EXISTS niveau_classe_id;
