ALTER TABLE classe
    ADD COLUMN annee_scolaire_id BIGINT UNSIGNED NOT NULL;
ALTER TABLE classe
    ADD CONSTRAINT fk_classe_annee_scolaire_id
    FOREIGN KEY (annee_scolaire_id)
    REFERENCES annee_scolaire (Id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT;
CREATE INDEX idx_classe_annee_scolaire_id ON classe (annee_scolaire_id);

ALTER TABLE classe
    ADD COLUMN niveau_classe_id BIGINT UNSIGNED NOT NULL;
ALTER TABLE classe
    ADD CONSTRAINT fk_classe_niveau_classe_id
    FOREIGN KEY (niveau_classe_id)
    REFERENCES niveau_classe (Id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT;
CREATE INDEX idx_classe_niveau_classe_id ON classe (niveau_classe_id);
