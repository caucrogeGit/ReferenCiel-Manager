-- Migration Forge
-- Version: 20260711144512
-- Name: create_auth_mfa
-- Source: opt-in forge-mvc-mfa (ADR-014)
-- Generated from: mvc/models/sql/auth_mfa_factors.sql + auth_mfa_recovery_codes.sql
--
-- Review this SQL before running:
-- forge migration:apply
-- NB commentaires ASCII sobres sans apostrophe (F27, retour-012).

-- Facteurs MFA (TOTP) : le secret est stocke CHIFFRE (prefixe enc, jamais en clair).
CREATE TABLE IF NOT EXISTS auth_mfa_factors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    factor_type VARCHAR(40) NOT NULL,
    totp_secret VARCHAR(255) NOT NULL,
    status VARCHAR(40) NOT NULL DEFAULT 'pending',
    label VARCHAR(120) NULL,
    confirmed_at DATETIME NULL,
    last_used_at DATETIME NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_auth_mfa_factors_user_id (user_id),
    INDEX idx_auth_mfa_factors_user_status (user_id, status),
    CONSTRAINT fk_auth_mfa_factors_user_id
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Codes de secours : seul le hash SHA-256 est conserve (jamais le code brut).
CREATE TABLE IF NOT EXISTS auth_mfa_recovery_codes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    code_hash CHAR(64) NOT NULL UNIQUE,
    used_at DATETIME NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_auth_mfa_recovery_codes_user_id (user_id),
    INDEX idx_auth_mfa_recovery_codes_used_at (used_at),
    CONSTRAINT fk_auth_mfa_recovery_codes_user_id
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
