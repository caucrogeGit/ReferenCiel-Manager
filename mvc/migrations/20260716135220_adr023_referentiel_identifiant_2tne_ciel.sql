-- Migration Forge
-- Version: 20260716135220
-- Name: adr023_referentiel_identifiant_2tne_ciel
-- Aligne l'identifiant du referentiel de la 2nde commune, option CIEL :
-- ciel-2tne -> 2tne-ciel (l'ordre 2tne-<option> vaut pour toutes les options TNE).
-- Les scenarios pointent par referentiel_id (FK), pas par l'identifiant : ils ne
-- bougent pas. Idempotent (WHERE cible ; no-op sur une base fraiche importee du JSON).

UPDATE referentiel_niveau_classe SET Identifiant = '2tne-ciel' WHERE Identifiant = 'ciel-2tne';
