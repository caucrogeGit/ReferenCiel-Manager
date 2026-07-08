ALTER TABLE classe
    ADD CONSTRAINT fk_classe_annee_scolaire_id
    FOREIGN KEY (annee_scolaire_id)
    REFERENCES annee_scolaire (Id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT;

ALTER TABLE classe
    ADD CONSTRAINT fk_classe_niveau_classe_id
    FOREIGN KEY (niveau_classe_id)
    REFERENCES niveau_classe (Id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT;
