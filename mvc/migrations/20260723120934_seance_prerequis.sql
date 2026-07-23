-- Migration Forge
-- Version: 20260723120934
-- Name: seance_prerequis
-- Champ « Prérequis » de la fiche de séance (retour porteur, montage de la
-- séance « La tension électrique ») : texte libre, facultatif, saisi dans le
-- tunnel après Thème/Durée. Ajouté au contrat Seance (prerequis).

ALTER TABLE seance ADD COLUMN Prerequis TEXT NULL AFTER DureeEstimeeMinutes;
