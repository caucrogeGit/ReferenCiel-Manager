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

ALTER TABLE referentiel_niveau_classe
    ADD CONSTRAINT fk_referentiel_niveau_classe_formation_id
    FOREIGN KEY (formation_id)
    REFERENCES formation (Id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT;

ALTER TABLE referentiel_niveau_classe
    ADD CONSTRAINT fk_referentiel_niveau_classe_niveau_classe_id
    FOREIGN KEY (niveau_classe_id)
    REFERENCES niveau_classe (Id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT;

ALTER TABLE pole_activite
    ADD CONSTRAINT fk_pole_activite_referentiel_id
    FOREIGN KEY (referentiel_id)
    REFERENCES referentiel_niveau_classe (Id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT;

ALTER TABLE activite_professionnelle
    ADD CONSTRAINT fk_activite_professionnelle_referentiel_id
    FOREIGN KEY (referentiel_id)
    REFERENCES referentiel_niveau_classe (Id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT;

ALTER TABLE activite_professionnelle
    ADD CONSTRAINT fk_activite_professionnelle_pole_id
    FOREIGN KEY (pole_id)
    REFERENCES pole_activite (Id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT;

ALTER TABLE tache
    ADD CONSTRAINT fk_tache_activite_id
    FOREIGN KEY (activite_id)
    REFERENCES activite_professionnelle (Id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT;

ALTER TABLE resultat_attendu
    ADD CONSTRAINT fk_resultat_attendu_activite_id
    FOREIGN KEY (activite_id)
    REFERENCES activite_professionnelle (Id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT;

ALTER TABLE competence
    ADD CONSTRAINT fk_competence_referentiel_id
    FOREIGN KEY (referentiel_id)
    REFERENCES referentiel_niveau_classe (Id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT;

ALTER TABLE connaissance
    ADD CONSTRAINT fk_connaissance_competence_id
    FOREIGN KEY (competence_id)
    REFERENCES competence (Id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT;

ALTER TABLE critere_observable
    ADD CONSTRAINT fk_critere_observable_competence_id
    FOREIGN KEY (competence_id)
    REFERENCES competence (Id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT;

ALTER TABLE indicateur_reussite
    ADD CONSTRAINT fk_indicateur_reussite_referentiel_id
    FOREIGN KEY (referentiel_id)
    REFERENCES referentiel_niveau_classe (Id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT;

ALTER TABLE famille_competence
    ADD CONSTRAINT fk_famille_competence_referentiel_id
    FOREIGN KEY (referentiel_id)
    REFERENCES referentiel_niveau_classe (Id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT;

ALTER TABLE source
    ADD CONSTRAINT fk_source_referentiel_id
    FOREIGN KEY (referentiel_id)
    REFERENCES referentiel_niveau_classe (Id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT;

CREATE TABLE IF NOT EXISTS activite_competence (
    id INT NOT NULL AUTO_INCREMENT,
    activite_professionnelle_id INT NOT NULL,
    competence_id INT NOT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_activite_competence (activite_professionnelle_id, competence_id),
    INDEX idx_activite_competence_activite_professionnelle_id (activite_professionnelle_id),
    INDEX idx_activite_competence_competence_id (competence_id),
    CONSTRAINT fk_activite_competence_activite_professionnelle_id
        FOREIGN KEY (activite_professionnelle_id)
        REFERENCES activite_professionnelle (id)
        ON DELETE CASCADE,
    CONSTRAINT fk_activite_competence_competence_id
        FOREIGN KEY (competence_id)
        REFERENCES competence (id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS cc_competence (
    id INT NOT NULL AUTO_INCREMENT,
    famille_competence_id INT NOT NULL,
    competence_id INT NOT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_cc_competence (famille_competence_id, competence_id),
    INDEX idx_cc_competence_famille_competence_id (famille_competence_id),
    INDEX idx_cc_competence_competence_id (competence_id),
    CONSTRAINT fk_cc_competence_famille_competence_id
        FOREIGN KEY (famille_competence_id)
        REFERENCES famille_competence (id)
        ON DELETE CASCADE,
    CONSTRAINT fk_cc_competence_competence_id
        FOREIGN KEY (competence_id)
        REFERENCES competence (id)
        ON DELETE CASCADE
);

ALTER TABLE scenario
    ADD CONSTRAINT fk_scenario_referentiel_id
    FOREIGN KEY (referentiel_id)
    REFERENCES referentiel_niveau_classe (Id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT;

ALTER TABLE scenario
    ADD CONSTRAINT fk_scenario_auteur_id
    FOREIGN KEY (auteur_id)
    REFERENCES professeur (Id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT;

CREATE TABLE IF NOT EXISTS scenario_professeur (
    id INT NOT NULL AUTO_INCREMENT,
    scenario_id INT NOT NULL,
    professeur_id INT NOT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_scenario_professeur (scenario_id, professeur_id),
    INDEX idx_scenario_professeur_scenario_id (scenario_id),
    INDEX idx_scenario_professeur_professeur_id (professeur_id),
    CONSTRAINT fk_scenario_professeur_scenario_id
        FOREIGN KEY (scenario_id)
        REFERENCES scenario (id)
        ON DELETE CASCADE,
    CONSTRAINT fk_scenario_professeur_professeur_id
        FOREIGN KEY (professeur_id)
        REFERENCES professeur (id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS scenario_competence (
    id INT NOT NULL AUTO_INCREMENT,
    scenario_id INT NOT NULL,
    competence_id INT NOT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_scenario_competence (scenario_id, competence_id),
    INDEX idx_scenario_competence_scenario_id (scenario_id),
    INDEX idx_scenario_competence_competence_id (competence_id),
    CONSTRAINT fk_scenario_competence_scenario_id
        FOREIGN KEY (scenario_id)
        REFERENCES scenario (id)
        ON DELETE CASCADE,
    CONSTRAINT fk_scenario_competence_competence_id
        FOREIGN KEY (competence_id)
        REFERENCES competence (id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS scenario_critere (
    id INT NOT NULL AUTO_INCREMENT,
    scenario_id INT NOT NULL,
    critere_observable_id INT NOT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_scenario_critere (scenario_id, critere_observable_id),
    INDEX idx_scenario_critere_scenario_id (scenario_id),
    INDEX idx_scenario_critere_critere_observable_id (critere_observable_id),
    CONSTRAINT fk_scenario_critere_scenario_id
        FOREIGN KEY (scenario_id)
        REFERENCES scenario (id)
        ON DELETE CASCADE,
    CONSTRAINT fk_scenario_critere_critere_observable_id
        FOREIGN KEY (critere_observable_id)
        REFERENCES critere_observable (id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS scenario_activite (
    id INT NOT NULL AUTO_INCREMENT,
    scenario_id INT NOT NULL,
    activite_professionnelle_id INT NOT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_scenario_activite (scenario_id, activite_professionnelle_id),
    INDEX idx_scenario_activite_scenario_id (scenario_id),
    INDEX idx_scenario_activite_activite_professionnelle_id (activite_professionnelle_id),
    CONSTRAINT fk_scenario_activite_scenario_id
        FOREIGN KEY (scenario_id)
        REFERENCES scenario (id)
        ON DELETE CASCADE,
    CONSTRAINT fk_scenario_activite_activite_professionnelle_id
        FOREIGN KEY (activite_professionnelle_id)
        REFERENCES activite_professionnelle (id)
        ON DELETE CASCADE
);

ALTER TABLE starter_welcome
    ADD CONSTRAINT fk_starter_welcome_niveau_classe_id
    FOREIGN KEY (niveau_classe_id)
    REFERENCES niveau_classe (Id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT;

ALTER TABLE version_starter
    ADD CONSTRAINT fk_version_starter_starter_id
    FOREIGN KEY (starter_id)
    REFERENCES starter_welcome (Id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT;

ALTER TABLE parcours
    ADD CONSTRAINT fk_parcours_niveau_classe_id
    FOREIGN KEY (niveau_classe_id)
    REFERENCES niveau_classe (Id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT;

ALTER TABLE version_parcours
    ADD CONSTRAINT fk_version_parcours_parcours_id
    FOREIGN KEY (parcours_id)
    REFERENCES parcours (Id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT;

ALTER TABLE palier
    ADD CONSTRAINT fk_palier_version_parcours_id
    FOREIGN KEY (version_parcours_id)
    REFERENCES version_parcours (Id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT;

ALTER TABLE affectation_parcours
    ADD CONSTRAINT fk_affectation_parcours_version_parcours_id
    FOREIGN KEY (version_parcours_id)
    REFERENCES version_parcours (Id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT;

ALTER TABLE affectation_parcours
    ADD CONSTRAINT fk_affectation_parcours_classe_id
    FOREIGN KEY (classe_id)
    REFERENCES classe (Id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT;

ALTER TABLE affectation_parcours
    ADD CONSTRAINT fk_affectation_parcours_professeur_id
    FOREIGN KEY (professeur_id)
    REFERENCES professeur (Id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT;

CREATE TABLE IF NOT EXISTS affectation_parcours_eleve (
    id INT NOT NULL AUTO_INCREMENT,
    affectation_parcours_id INT NOT NULL,
    eleve_id INT NOT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_affectation_parcours_eleve (affectation_parcours_id, eleve_id),
    INDEX idx_affectation_parcours_eleve_affectation_parcours_id (affectation_parcours_id),
    INDEX idx_affectation_parcours_eleve_eleve_id (eleve_id),
    CONSTRAINT fk_affectation_parcours_eleve_affectation_parcours_id
        FOREIGN KEY (affectation_parcours_id)
        REFERENCES affectation_parcours (id)
        ON DELETE CASCADE,
    CONSTRAINT fk_affectation_parcours_eleve_eleve_id
        FOREIGN KEY (eleve_id)
        REFERENCES eleve (id)
        ON DELETE CASCADE
);

ALTER TABLE progression_eleve
    ADD CONSTRAINT fk_progression_eleve_eleve_id
    FOREIGN KEY (eleve_id)
    REFERENCES eleve (Id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT;

ALTER TABLE progression_eleve
    ADD CONSTRAINT fk_progression_eleve_affectation_parcours_id
    FOREIGN KEY (affectation_parcours_id)
    REFERENCES affectation_parcours (Id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT;

ALTER TABLE progression_palier
    ADD CONSTRAINT fk_progression_palier_progression_eleve_id
    FOREIGN KEY (progression_eleve_id)
    REFERENCES progression_eleve (Id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT;

ALTER TABLE progression_palier
    ADD CONSTRAINT fk_progression_palier_palier_id
    FOREIGN KEY (palier_id)
    REFERENCES palier (Id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT;

ALTER TABLE qcm
    ADD CONSTRAINT fk_qcm_palier_id
    FOREIGN KEY (palier_id)
    REFERENCES palier (Id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT;

ALTER TABLE question_qcm
    ADD CONSTRAINT fk_question_qcm_qcm_id
    FOREIGN KEY (qcm_id)
    REFERENCES qcm (Id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT;

ALTER TABLE choix_qcm
    ADD CONSTRAINT fk_choix_qcm_question_id
    FOREIGN KEY (question_id)
    REFERENCES question_qcm (Id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT;

ALTER TABLE tentative_qcm
    ADD CONSTRAINT fk_tentative_qcm_progression_palier_id
    FOREIGN KEY (progression_palier_id)
    REFERENCES progression_palier (Id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT;

ALTER TABLE reponse_qcm
    ADD CONSTRAINT fk_reponse_qcm_tentative_id
    FOREIGN KEY (tentative_id)
    REFERENCES tentative_qcm (Id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT;

ALTER TABLE reponse_qcm
    ADD CONSTRAINT fk_reponse_qcm_question_id
    FOREIGN KEY (question_id)
    REFERENCES question_qcm (Id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT;

ALTER TABLE reponse_qcm
    ADD CONSTRAINT fk_reponse_qcm_choix_id
    FOREIGN KEY (choix_id)
    REFERENCES choix_qcm (Id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT;

ALTER TABLE checklist
    ADD CONSTRAINT fk_checklist_palier_id
    FOREIGN KEY (palier_id)
    REFERENCES palier (Id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT;

ALTER TABLE section_checklist
    ADD CONSTRAINT fk_section_checklist_checklist_id
    FOREIGN KEY (checklist_id)
    REFERENCES checklist (Id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT;

ALTER TABLE item_checklist
    ADD CONSTRAINT fk_item_checklist_section_id
    FOREIGN KEY (section_id)
    REFERENCES section_checklist (Id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT;

ALTER TABLE item_coche
    ADD CONSTRAINT fk_item_coche_item_id
    FOREIGN KEY (item_id)
    REFERENCES item_checklist (Id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT;

ALTER TABLE item_coche
    ADD CONSTRAINT fk_item_coche_progression_palier_id
    FOREIGN KEY (progression_palier_id)
    REFERENCES progression_palier (Id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT;

ALTER TABLE activite
    ADD CONSTRAINT fk_activite_palier_id
    FOREIGN KEY (palier_id)
    REFERENCES palier (Id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT;

ALTER TABLE depot_eleve
    ADD CONSTRAINT fk_depot_eleve_progression_palier_id
    FOREIGN KEY (progression_palier_id)
    REFERENCES progression_palier (Id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT;

ALTER TABLE depot_eleve
    ADD CONSTRAINT fk_depot_eleve_activite_id
    FOREIGN KEY (activite_id)
    REFERENCES activite (Id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT;

ALTER TABLE evaluation_activite
    ADD CONSTRAINT fk_evaluation_activite_progression_palier_id
    FOREIGN KEY (progression_palier_id)
    REFERENCES progression_palier (Id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT;

ALTER TABLE evaluation_activite
    ADD CONSTRAINT fk_evaluation_activite_activite_id
    FOREIGN KEY (activite_id)
    REFERENCES activite (Id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT;

ALTER TABLE evaluation_activite
    ADD CONSTRAINT fk_evaluation_activite_professeur_id
    FOREIGN KEY (professeur_id)
    REFERENCES professeur (Id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT;

ALTER TABLE evaluation_critere
    ADD CONSTRAINT fk_evaluation_critere_evaluation_activite_id
    FOREIGN KEY (evaluation_activite_id)
    REFERENCES evaluation_activite (Id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT;

ALTER TABLE evaluation_critere
    ADD CONSTRAINT fk_evaluation_critere_critere_id
    FOREIGN KEY (critere_id)
    REFERENCES critere_observable (Id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT;

ALTER TABLE bilan_eleve
    ADD CONSTRAINT fk_bilan_eleve_eleve_id
    FOREIGN KEY (eleve_id)
    REFERENCES eleve (Id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT;

ALTER TABLE bilan_eleve
    ADD CONSTRAINT fk_bilan_eleve_professeur_id
    FOREIGN KEY (professeur_id)
    REFERENCES professeur (Id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT;

ALTER TABLE bilan_eleve
    ADD CONSTRAINT fk_bilan_eleve_progression_eleve_id
    FOREIGN KEY (progression_eleve_id)
    REFERENCES progression_eleve (Id)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT;
