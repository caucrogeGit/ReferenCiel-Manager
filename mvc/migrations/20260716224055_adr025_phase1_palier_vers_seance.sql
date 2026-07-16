-- Migration Forge
-- Version: 20260716224055
-- Name: adr025_phase1_palier_vers_seance
-- ADR-025 phase 1 : renommage Palier -> Seance (sémantique Éducation nationale,
-- un palier se nomme séance). Table palier -> seance ; les dépendants activite,
-- checklist, dossier_technique et progression_palier voient leur FK
-- palier_id -> seance_id. Les colonnes progression_palier_id (dépendantes de
-- ProgressionPalier) relèvent de la phase 2. Même pattern que etape6b.

RENAME TABLE palier TO seance;

-- FK sortante de la table renommée : le nom de contrainte suit la table.
ALTER TABLE seance DROP FOREIGN KEY IF EXISTS fk_palier_parcours_id;
ALTER TABLE seance DROP INDEX IF EXISTS fk_palier_parcours_id;
ALTER TABLE seance
    ADD CONSTRAINT fk_seance_parcours_id
        FOREIGN KEY (parcours_id) REFERENCES parcours (Id)
        ON DELETE RESTRICT ON UPDATE RESTRICT;

-- Activite -> Seance
ALTER TABLE activite DROP FOREIGN KEY IF EXISTS fk_activite_palier_id;
ALTER TABLE activite DROP INDEX IF EXISTS fk_activite_palier_id;
ALTER TABLE activite CHANGE COLUMN palier_id seance_id BIGINT UNSIGNED NOT NULL;
ALTER TABLE activite
    ADD CONSTRAINT fk_activite_seance_id
        FOREIGN KEY (seance_id) REFERENCES seance (Id)
        ON DELETE RESTRICT ON UPDATE RESTRICT;

-- Checklist -> Seance
ALTER TABLE checklist DROP FOREIGN KEY IF EXISTS fk_checklist_palier_id;
ALTER TABLE checklist DROP INDEX IF EXISTS fk_checklist_palier_id;
ALTER TABLE checklist CHANGE COLUMN palier_id seance_id BIGINT UNSIGNED NOT NULL;
ALTER TABLE checklist
    ADD CONSTRAINT fk_checklist_seance_id
        FOREIGN KEY (seance_id) REFERENCES seance (Id)
        ON DELETE RESTRICT ON UPDATE RESTRICT;

-- DossierTechnique -> Seance
ALTER TABLE dossier_technique DROP FOREIGN KEY IF EXISTS fk_dossier_technique_palier_id;
ALTER TABLE dossier_technique DROP INDEX IF EXISTS fk_dossier_technique_palier_id;
ALTER TABLE dossier_technique CHANGE COLUMN palier_id seance_id BIGINT UNSIGNED NOT NULL;
ALTER TABLE dossier_technique
    ADD CONSTRAINT fk_dossier_technique_seance_id
        FOREIGN KEY (seance_id) REFERENCES seance (Id)
        ON DELETE CASCADE ON UPDATE RESTRICT;

-- ProgressionPalier -> Seance (la table progression_palier sera renommée en phase 2)
ALTER TABLE progression_palier DROP FOREIGN KEY IF EXISTS fk_progression_palier_palier_id;
ALTER TABLE progression_palier DROP INDEX IF EXISTS fk_progression_palier_palier_id;
ALTER TABLE progression_palier CHANGE COLUMN palier_id seance_id BIGINT UNSIGNED NOT NULL;
ALTER TABLE progression_palier
    ADD CONSTRAINT fk_progression_palier_seance_id
        FOREIGN KEY (seance_id) REFERENCES seance (Id)
        ON DELETE RESTRICT ON UPDATE RESTRICT;
