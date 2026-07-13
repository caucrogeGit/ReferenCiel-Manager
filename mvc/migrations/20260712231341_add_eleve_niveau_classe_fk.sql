-- Migration Forge
-- Version: 20260712231341
-- Name: add_eleve_niveau_classe_fk
-- Lie un Eleve a son niveau de classe (many_to_one, obligatoire) : un eleve a
-- exactement un niveau_classe et un niveau_classe compte 0 a n eleves. La colonne
-- suit la convention des FK generees (snake_case, cf. inscription_eleve.eleve_id).
--
-- Ajout en trois temps pour rester applicable sur une base contenant deja des
-- eleves : colonne nullable, backfill sur le niveau existant, puis NOT NULL et FK.
-- Precondition du backfill : au moins un niveau_classe present (importe via le
-- referentiel). Sur une base vierge la table eleve est vide et l ordre est neutre.

-- 1) Colonne nullable (aucune valeur par defaut imposee aux lignes existantes).
ALTER TABLE eleve ADD COLUMN niveau_classe_id BIGINT UNSIGNED NULL;

-- 2) Backfill : rattache les eleves existants au niveau_classe deja en base.
UPDATE eleve
   SET niveau_classe_id = (SELECT Id FROM niveau_classe ORDER BY Id LIMIT 1)
 WHERE niveau_classe_id IS NULL;

-- 3) Contrainte NOT NULL (un et un seul niveau) puis cle etrangere.
ALTER TABLE eleve MODIFY niveau_classe_id BIGINT UNSIGNED NOT NULL;

ALTER TABLE eleve
    ADD CONSTRAINT fk_eleve_niveau_classe_id
    FOREIGN KEY (niveau_classe_id) REFERENCES niveau_classe(Id);
