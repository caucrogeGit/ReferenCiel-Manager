# ADR-015 — MFA TOTP optionnelle (sécurité applicative réelle, T2)

**Statut :** Accepté
**Date :** 2026-07-11

## Contexte

L'[ADR-014](014-securite-applicative-reelle.md) trace la trajectoire de la sécurité
applicative réelle et renvoie la **MFA** (temps T2) à un ADR dédié. Le cadrage
l'exige : « les comptes professeur et administrateur **doivent pouvoir utiliser la
MFA** » (instructions §20, cadre §10).

L'opt-in officiel **`forge-mvc-mfa`** 1.0.0rc2 est installé. C'est une **bibliothèque
pure** (kind `crosscutting`) : elle fournit toute la logique (TOTP, codes de secours,
challenge de session, chiffrement du secret, anti-rejeu) **sans** routes, commandes,
ni accès base. Comme pour le RBAC ([ADR-013](013-rbac-couche-fine-maison-sur-contrat.md))
et les sessions, **l'application câble** : persistance (SQL), routes, contrôleurs,
vues, configuration.

Le DDL des deux tables (`auth_mfa_factors`, `auth_mfa_recovery_codes`) existe déjà
sous `mvc/models/sql/` mais **n'est pas migré** (le socle auth l'a délibérément omis).

## Décision

1. **MFA optionnelle, en self-service.** Chaque utilisateur connecté active (ou
   désactive) sa MFA depuis une page **« Sécurité »** (`/securite`). Cela satisfait
   le « doivent pouvoir » du cadrage sans imposer de friction. Le login ne déclenche
   un challenge **que si** l'utilisateur a un facteur TOTP actif.

2. **Facteurs : TOTP + codes de secours.** Enrôlement TOTP (QR / URI `otpauth://`
   confirmé par un premier code), et **10 codes de secours** affichés **une seule
   fois** à l'activation. Le challenge de login accepte un code TOTP **ou** un code
   de secours (un authenticator perdu ne bloque pas le compte).

3. **Réutiliser l'opt-in, ne rien réimplémenter.** Enrôlement via
   `create_totp_factor` → `confirm_totp_factor` ; secours via `create_recovery_codes`
   / `consume_recovery_code` ; challenge via `start_mfa_challenge` /
   `verify_mfa_challenge`. L'app ne fait que la **persistance** (SQL visible et
   paramétré) et le câblage HTTP.

4. **Secret TOTP chiffré au repos.** Le secret n'est **jamais** stocké en clair :
   l'opt-in le chiffre (Fernet, préfixe `enc:`). La clé vit dans la variable d'env
   **`FORGE_MFA_SECRET_KEY`** (hors dépôt : `env/dev` ignoré par git, `env/prod` en
   production ; `env/example` documente la génération). La validité de la clé est
   vérifiée **au moment de l'usage** (enrôlement / challenge) — la MFA étant
   optionnelle, une clé absente ne bloque pas le reste de l'application.

5. **Challenge au login (anti-fixation préservée).** Après le mot de passe validé :
   si un facteur MFA est actif, on **ne connecte pas** encore — on démarre un
   challenge (`start_mfa_challenge`, user_id en session seulement) et on redirige
   vers `/login/mfa`. À la vérification réussie : `login_user` **puis**
   `regenerate_session` (même défense anti-fixation que le login simple). Le
   rate-limit (5 essais / 300 s) et l'anti-rejeu sont assurés en interne par l'opt-in.

6. **Audit.** Les événements `AUTH_EVENT_MFA_REQUIRED` / `_CHALLENGE_SUCCESS` /
   `_CHALLENGE_FAILED` sont émis autour du flux (table `auth_audit_log`, déjà migrée).

7. **Step-up sur la désactivation.** Retirer la MFA est une action sensible : elle
   exige une **re-preuve du 2ᵉ facteur** (code TOTP ou de secours), valable 10 min
   (fenêtre de revalidation). On utilise l'**API native** de l'opt-in
   (`verify_mfa_revalidation` / `has_recent_mfa_revalidation`).

   > *Historique* : au premier incrément, cette API était inutilisable avec l'auth
   > moderne (session dépréciée, [retour-019](../banc-essai/retour-019-mfa-revalidation-step-up-session-depreciee.md)
   > / F42) et on la contournait par une vérification directe du facteur. **F42 corrigé
   > côté Forge (sha `6927a266`, 2026-07-12), le contournement a été retiré** au profit
   > de l'API native.

8. **Différé (incréments ultérieurs).** Le durcissement multi-worker de l'anti-rejeu
   et l'obligation de MFA (au lieu de l'option) restent hors périmètre tant que le
   besoin ne l'impose pas.

## Conséquences

- **Positif** : capacité MFA réelle (exigence cadrage §20), robuste (codes de
  secours), secret chiffré au repos, réutilisation intégrale de l'opt-in, isolée et
  réversible. Les tables MFA sont enfin migrées.
- **Négatif / limites** : l'anti-rejeu de l'opt-in est **in-memory process-local**
  (non partagé entre workers) — limitation assumée, fenêtre de risque < 30 s. La
  clé `FORGE_MFA_SECRET_KEY` doit être **gérée** (rotation = ré-enrôlement des
  facteurs, car les secrets existants deviennent indéchiffrables).
- **Réversibilité** : opt-in débranché via `optins/registry.py` ; le code MFA est
  isolé (`securite_controller`, `mfa_model`, routes `/securite` + `/login/mfa`).

## Alternatives écartées

- **MFA obligatoire pour prof/admin.** Rejetée pour ce premier incrément : impose un
  état « enrôlement requis » dans le flux de login et de la friction, au-delà du
  « doivent pouvoir » du cadrage. Réexaminable si une politique l'exige.
- **TOTP seul, sans codes de secours.** Rejetée : un authenticator perdu bloquerait
  le compte (récupération seulement par un admin). Le coût des codes de secours est
  faible (l'opt-in les fournit) pour un gain de robustesse important.
- **Réimplémenter TOTP/chiffrement à la main.** Rejetée : l'opt-in officiel est
  audité et couvre rate-limit, anti-rejeu, chiffrement ; le réécrire violerait la
  règle « 100 % Forge » et introduirait du risque cryptographique.
