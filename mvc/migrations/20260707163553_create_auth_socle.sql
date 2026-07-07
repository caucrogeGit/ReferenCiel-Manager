-- Migration Forge
-- Version: 20260707163553
-- Name: create_auth_socle
--
-- Socle Auth/User (ticket 07), source : mvc/models/sql/ (forge auth:init).
-- RBAC et MFA DIFFÉRÉS (garde-fou « différer RBAC/MFA ≠ désactiver l'auth ») :
--   - user_roles  OMIS : FK vers `roles`, table de l'opt-in rbac (non installé) ;
--   - auth_mfa_*  OMIS : MFA différée (opt-in mfa non installé).
-- Rappel : forge db:apply n'applique PAS mvc/models/sql/ — voir banc-essai/retour-006.
-- Ordre : users d'abord (les autres tables y référencent user_id).

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    email_verified_at DATETIME NULL,
    last_login_at DATETIME NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS auth_tokens (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    purpose VARCHAR(80) NOT NULL,
    token_hash CHAR(64) NOT NULL UNIQUE,
    expires_at DATETIME NOT NULL,
    used_at DATETIME NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_auth_tokens_user_purpose (user_id, purpose),
    INDEX idx_auth_tokens_expires_at (expires_at),
    CONSTRAINT fk_auth_tokens_user_id
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS auth_audit_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    event_type VARCHAR(120) NOT NULL,
    user_id INT NULL,
    actor_user_id INT NULL,
    ip_address VARCHAR(45) NULL,
    user_agent VARCHAR(255) NULL,
    metadata_json TEXT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_auth_audit_log_event_type (event_type),
    INDEX idx_auth_audit_log_user_id (user_id),
    INDEX idx_auth_audit_log_actor_user_id (actor_user_id),
    INDEX idx_auth_audit_log_created_at (created_at),
    CONSTRAINT fk_auth_audit_log_user_id
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE SET NULL,
    CONSTRAINT fk_auth_audit_log_actor_user_id
        FOREIGN KEY (actor_user_id)
        REFERENCES users(id)
        ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS auth_rate_limit_attempts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    action VARCHAR(120) NOT NULL,
    rate_key VARCHAR(255) NOT NULL,
    ip_address VARCHAR(45) NULL,
    user_id INT NULL,
    success BOOLEAN NOT NULL DEFAULT FALSE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_auth_rate_limit_action_key (action, rate_key),
    INDEX idx_auth_rate_limit_created_at (created_at),
    INDEX idx_auth_rate_limit_user_id (user_id),
    CONSTRAINT fk_auth_rate_limit_user_id
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
