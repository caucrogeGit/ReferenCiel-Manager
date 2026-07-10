-- Migration Forge
-- Version: 20260710195527
-- Name: align_forge_sessions_v2
--
-- Aligne forge_sessions (creee par 20260710171739, DDL notice rc2) sur le schema
-- durci de forge-mvc-sessions-db, retour terrain 016 F36/F37 et ADR-071.
--
-- 1. Concurrence optimiste F36 : le store garde chaque ecriture par
--    WHERE session_id = ? AND version = ? et incremente version. La colonne
--    version manquait, sans elle le store durci echoue (Unknown column).
-- 2. Horodatages F37 : Python devient seule autorite (UTC), le store ecrit
--    created_at/updated_at explicitement. On retire les defauts SGBD
--    (DEFAULT CURRENT_TIMESTAMP et ON UPDATE) pour lever la double horloge.
--
-- Note : commentaire sans point-virgule ni apostrophe (decoupeur SQL Forge,
-- retour terrain 012).

ALTER TABLE forge_sessions
    ADD COLUMN version INT NOT NULL DEFAULT 0 AFTER expire_at,
    MODIFY created_at DATETIME NOT NULL,
    MODIFY updated_at DATETIME NOT NULL;
