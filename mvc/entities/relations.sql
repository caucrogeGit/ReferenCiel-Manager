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

ALTER TABLE inscription_eleve
    ADD CONSTRAINT fk_inscription_eleve_eleve_id
    FOREIGN KEY (eleve_id)
    REFERENCES eleve (Id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT;

ALTER TABLE inscription_eleve
    ADD CONSTRAINT fk_inscription_eleve_classe_id
    FOREIGN KEY (classe_id)
    REFERENCES classe (Id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT;

ALTER TABLE inscription_eleve
    ADD CONSTRAINT fk_inscription_eleve_annee_scolaire_id
    FOREIGN KEY (annee_scolaire_id)
    REFERENCES annee_scolaire (Id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT;

ALTER TABLE affectation_professeur_classe
    ADD CONSTRAINT fk_affectation_professeur_classe_professeur_id
    FOREIGN KEY (professeur_id)
    REFERENCES professeur (Id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT;

ALTER TABLE affectation_professeur_classe
    ADD CONSTRAINT fk_affectation_professeur_classe_classe_id
    FOREIGN KEY (classe_id)
    REFERENCES classe (Id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT;

ALTER TABLE affectation_professeur_classe
    ADD CONSTRAINT fk_affectation_professeur_classe_annee_scolaire_id
    FOREIGN KEY (annee_scolaire_id)
    REFERENCES annee_scolaire (Id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT;

ALTER TABLE groupe
    ADD CONSTRAINT fk_groupe_classe_id
    FOREIGN KEY (classe_id)
    REFERENCES classe (Id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT;

CREATE TABLE IF NOT EXISTS groupe_eleve (
    id INT NOT NULL AUTO_INCREMENT,
    groupe_id INT NOT NULL,
    eleve_id INT NOT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_groupe_eleve (groupe_id, eleve_id),
    INDEX idx_groupe_eleve_groupe_id (groupe_id),
    INDEX idx_groupe_eleve_eleve_id (eleve_id),
    CONSTRAINT fk_groupe_eleve_groupe_id
        FOREIGN KEY (groupe_id)
        REFERENCES groupe (id)
        ON DELETE CASCADE,
    CONSTRAINT fk_groupe_eleve_eleve_id
        FOREIGN KEY (eleve_id)
        REFERENCES eleve (id)
        ON DELETE CASCADE
);
