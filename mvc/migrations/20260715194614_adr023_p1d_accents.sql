-- Migration Forge
-- Version: 20260715194614
-- Name: adr023_p1d_accents
-- ADR-023 phase 1d : les libelles crees en 1b l'ont ete en ASCII par prudence.
-- On retablit les accents (la base est utf8mb4, comme le reste des donnees).
-- Idempotent (UPDATE cibles par Code).

UPDATE formation
    SET Intitule = 'Métiers des transitions numérique et énergétique'
    WHERE Code = '2TNE';

UPDATE niveau_classe
    SET Intitule = 'Première professionnelle'
    WHERE Code = 'PREMIERE_PRO';

UPDATE formation_niveau
    SET Libelle = 'Seconde professionnelle, famille des métiers des transitions numérique et énergétique'
    WHERE Code = '2TNE';

UPDATE formation_niveau
    SET Libelle = 'Première Bac Pro CIEL'
    WHERE Code = '1CIEL';
