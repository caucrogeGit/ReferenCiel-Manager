-- Migration Forge
-- Version: 20260716170705
-- Name: adr022_critere_savoir_etre
-- Un critère observable peut être un « savoir-être » (comportemental), rendu en
-- italique dans le tunnel. Champ booléen, défaut 0 (les critères existants sont
-- techniques ; la valeur réelle vient du canonique au ré-import).
-- Idempotent (IF NOT EXISTS).

ALTER TABLE critere_observable ADD COLUMN IF NOT EXISTS SavoirEtre BOOLEAN NOT NULL DEFAULT 0 AFTER Libelle;
