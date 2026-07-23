-- Choix d'organisation des séances OBLIGATOIRE et conscient (retour porteur,
-- complément ADR-034) : les deux drapeaux deviennent NULLABLE. NULL/NULL =
-- « à préciser » ; le professeur doit choisir (libre, imposé, glissante) pour
-- finaliser la séquence. Les lignes existantes repassent « à préciser » :
-- leur « libre » n'était qu'un défaut, jamais un choix.
ALTER TABLE sequence
    MODIFY ActiviteGlissante TINYINT(1) NULL,
    MODIFY OrdreImpose TINYINT(1) NULL;
UPDATE sequence SET ActiviteGlissante = NULL, OrdreImpose = NULL;
