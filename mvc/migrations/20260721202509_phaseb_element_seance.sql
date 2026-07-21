-- Migration Forge
-- Version: 20260721202509
-- Name: phaseb_element_seance
-- ADR-032 phase B : ElementSeance, déroulé ordonné d'une séance. Polymorphe :
-- contenu libre ou référence à un QCM/checklist existants. Types réels
-- (Id BIGINT UNSIGNED). FK séance CASCADE (les éléments partent avec la séance) ;
-- FK qcm/checklist SET NULL (l'élément survit si l'objet référencé est supprimé).

CREATE TABLE IF NOT EXISTS element_seance (
    Id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    Ordre INT NOT NULL,
    Type VARCHAR(30) NOT NULL,
    Titre VARCHAR(200) NOT NULL,
    Contenu TEXT NULL,
    DureeMinutes INT NULL,
    Obligatoire TINYINT(1) NOT NULL DEFAULT 1,
    RolePedagogique VARCHAR(60) NULL,
    seance_id BIGINT UNSIGNED NOT NULL,
    qcm_id BIGINT UNSIGNED NULL,
    checklist_id BIGINT UNSIGNED NULL,
    CreatedAt DATETIME NOT NULL,
    UpdatedAt DATETIME NOT NULL,
    PRIMARY KEY (Id),
    INDEX idx_element_seance_seance_id (seance_id),
    INDEX idx_element_seance_qcm_id (qcm_id),
    INDEX idx_element_seance_checklist_id (checklist_id),
    CONSTRAINT fk_element_seance_seance_id
        FOREIGN KEY (seance_id) REFERENCES seance (Id) ON DELETE CASCADE,
    CONSTRAINT fk_element_seance_qcm_id
        FOREIGN KEY (qcm_id) REFERENCES qcm (Id) ON DELETE SET NULL,
    CONSTRAINT fk_element_seance_checklist_id
        FOREIGN KEY (checklist_id) REFERENCES checklist (Id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
