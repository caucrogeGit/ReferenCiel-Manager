-- Migration Forge
-- Version: 20260719225120
-- Name: seq02_drop_savoir_associe
-- ADR-028 : retrait de savoir_associe. La liste de savoirs en texte libre était
-- un doublon appauvri de l'entité Connaissance (ancrée au référentiel). Les
-- connaissances associées passent désormais par Connaissance et un lien
-- Séquence ↔ Connaissance. La table est vierge : aucune donnée perdue.

DROP TABLE IF EXISTS savoir_associe;
