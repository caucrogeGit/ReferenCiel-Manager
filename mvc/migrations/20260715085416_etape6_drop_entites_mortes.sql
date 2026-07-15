-- Migration Forge
-- Version: 20260715085416
-- Name: etape6_drop_entites_mortes
-- ADR-022 etape 6 : suppression des entites rendues mortes par l'aplatissement.
--   - StarterWelcome + VersionStarter : couche gabarit au-dessus du parcours
--   - VersionParcours : versionnement du parcours (paliers desormais sous parcours)
--   - AffectationParcours (+ pivot) : fusionnee dans la progression
--   - InscriptionEleve : remplacee par eleve.classe_id
--   - AffectationProfesseurClasse : remplacee par le pivot classe_professeur
-- Plus rien ne les reference (etapes 1-5). FK checks off le temps des DROP.

SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS affectation_parcours_eleve;
DROP TABLE IF EXISTS affectation_parcours;
DROP TABLE IF EXISTS version_parcours;
DROP TABLE IF EXISTS version_starter;
DROP TABLE IF EXISTS starter_welcome;
DROP TABLE IF EXISTS inscription_eleve;
DROP TABLE IF EXISTS affectation_professeur_classe;

SET FOREIGN_KEY_CHECKS = 1;
