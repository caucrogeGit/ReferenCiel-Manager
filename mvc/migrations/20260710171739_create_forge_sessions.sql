-- Migration Forge
-- Version: 20260710171739
-- Name: create_forge_sessions
--
-- Table requise par l'opt-in forge-mvc-sessions-db (DbSessionStore, ADR-054).
-- Store de session persistant, adossé à la base : sessions partagées entre
-- workers et conservées au redémarrage (le cœur ne fournit que MemorySessionStore
-- et FileSessionStore). Schéma variante MariaDB, fourni par la doc de l'opt-in.
-- Purge des sessions expirées : à câbler via DbSessionStore.cleanup_expired().

CREATE TABLE IF NOT EXISTS forge_sessions (
    session_id CHAR(64)  NOT NULL,
    data       LONGTEXT  NOT NULL,
    expire_at  DATETIME  NOT NULL,
    created_at DATETIME  NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME  NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (session_id),
    INDEX idx_forge_sessions_expire_at (expire_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
