-- Migration Forge
-- Version: 20260715074347
-- Name: etape1_parcours_canonique
-- ADR-022 etape 1 : Parcours devient l'objet canonique. Il absorbe l'identite
-- du starter (Identifiant, Presentation, Statut, ActiviteGlissante, OrdreImpose)
-- et se rattache directement au NiveauClasse ; il abandonne la derivation
-- version_starter_id. La branche pedagogique (bloc_b) a ete videe au prealable,
-- la table est vide : les colonnes NOT NULL s'ajoutent sans conflit.

ALTER TABLE parcours
    ADD COLUMN Identifiant VARCHAR(100) NOT NULL AFTER Id,
    ADD COLUMN Presentation TEXT NULL AFTER Titre,
    ADD COLUMN Statut VARCHAR(20) NOT NULL AFTER Presentation,
    ADD COLUMN ActiviteGlissante TINYINT(1) NOT NULL AFTER Statut,
    ADD COLUMN OrdreImpose TINYINT(1) NOT NULL AFTER ActiviteGlissante,
    ADD COLUMN niveau_classe_id BIGINT UNSIGNED NOT NULL AFTER OrdreImpose,
    ADD UNIQUE KEY uq_parcours_identifiant (Identifiant);

ALTER TABLE parcours
    DROP FOREIGN KEY fk_parcours_version_starter_id,
    DROP COLUMN version_starter_id;

ALTER TABLE parcours
    ADD CONSTRAINT fk_parcours_niveau_classe_id
        FOREIGN KEY (niveau_classe_id)
        REFERENCES niveau_classe (Id)
        ON DELETE RESTRICT
        ON UPDATE RESTRICT;
