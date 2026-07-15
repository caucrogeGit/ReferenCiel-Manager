-- Migration Forge
-- Version: 20260715193532
-- Name: adr023_p1c_referentiel_sur_formation
-- ADR-023 phase 1c : le referentiel appartient a la FORMATION, plus au niveau.
--   - le referentiel ciel-2tne est la 2nde commune : on le rattache a la
--     formation famille 2TNE (et non plus a la specialite Bac Pro CIEL) ;
--   - on retire la colonne niveau_classe_id.
-- L'unique composite uq_rnc_formation_niveau_version (formation_id,
-- niveau_classe_id, Version) reference la colonne a supprimer ET sert d'index de
-- tete a la FK formation_id : on cree d'abord un index de remplacement sur
-- formation_id, puis on droppe le composite, la FK niveau et la colonne.
-- Idempotent (UPDATE cible, IF [NOT] EXISTS).

-- 1) Re-scope : referentiel de 2nde commune -> formation famille 2TNE.
UPDATE referentiel_niveau_classe r
    JOIN formation f ON f.Code = '2TNE'
    SET r.formation_id = f.Id
    WHERE r.Identifiant = 'ciel-2tne';

-- 2) Index de remplacement pour la FK formation_id (avant de dropper le composite).
CREATE INDEX IF NOT EXISTS idx_rnc_formation_id ON referentiel_niveau_classe (formation_id);

-- 3) Drop de l'unique composite obsolete (il portait le niveau).
ALTER TABLE referentiel_niveau_classe DROP INDEX IF EXISTS uq_rnc_formation_niveau_version;

-- 4) Retrait du rattachement au niveau (FK deja tombee au 1er essai, IF EXISTS) + colonne.
ALTER TABLE referentiel_niveau_classe DROP FOREIGN KEY IF EXISTS fk_referentiel_niveau_classe_niveau_classe_id;
ALTER TABLE referentiel_niveau_classe DROP COLUMN IF EXISTS niveau_classe_id;
