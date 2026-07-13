# ADR-014 : Sécurité applicative réelle (trajectoire post-tunnel)

**Statut :** Accepté
**Date :** 2026-07-11

## Contexte

La section « Après le tunnel » de [`docs/tickets/README.md`](../tickets/README.md)
diffère la **sécurité applicative réelle** (`CompteUtilisateur`, connexion
applicative, RBAC, MFA, permissions réelles, lien `CompteUtilisateur` ↔ `Eleve`)
« à ouvrir par un ADR dédié le moment venu ».
Cet ADR est cette ouverture.

Une cartographie de l'existant montre que **la sécurité de base est déjà livrée** :
l'écart entre la doc (« différé ») et le code (« fait ») doit être acté.

### Ce qui EXISTE déjà et fonctionne

- **Authentification** : login/logout sur le socle `users`, hash de mot de passe
  (`core.auth.password`), rotation anti-fixation au login (`regenerate_session`).
- **Sessions** : persistées en base (opt-in `sessions-db`, ADR-071 / retour-016),
  cookies durcis (`__Host-session_id`, HttpOnly, SameSite=Strict, Secure), TTL 1 h.
- **RBAC** : couche fine maison ([ADR-013](013-rbac-couche-fine-maison-sur-contrat.md)),
  routes gardées par `guard_prefix`, nav filtrée par `can()`, contrat `rbac.json`.
- **Lien compte ↔ Eleve/Professeur** : colonne `UserId`, comptes créés par l'admin,
  **filtrage row-level** (`/mon-parcours` élève, `/mes-classes` professeur).
- **CSRF** actif par défaut sur toutes les routes non-sûres (y compris `/login`).
- **CSP + HSTS + en-têtes de sécurité** posés sur chaque réponse ; SSL en dev.

### Ce qui MANQUE ou reste différé

- **MFA** (prof/admin) : opt-in `forge-mvc-mfa` non installé, table `auth_mfa_*`
  non migrée.
  Exigé par le cadrage (§20, cadre §10).
- **Permissions fines** : le RBAC est **grossier par domaine** (assumé ADR-013),
  alors que le cadrage §19 liste des permissions **par action**.
- **Réinitialisation de mot de passe** : le cœur fournit tout (`core.auth.reset`,
  table `auth_tokens` provisionnée) mais **rien n'est branché** dans l'app.
- **Politique de mot de passe à la création** : `validate_new_password` (min 8,
  max borné) n'est appelée qu'au reset, pas à la **création de compte**, un
  compte peut aujourd'hui recevoir un mot de passe trivial.
- **Self-registration** : absente, création par l'admin uniquement (assumé).

## Décision

1. **Acter l'existant.** La sécurité de base (auth, sessions durcies, RBAC ADR-013,
   liens comptes + row-level, CSRF, CSP) est **en place et considérée acquise**.
   La
   mention « différé » du README pour ces éléments est **périmée** : le README est
   mis à jour pour refléter le code.

2. **Trajectoire en trois temps**, par valeur/coût décroissants :

   - **T1 : Durcissement des mots de passe (maintenant, cet ADR).** Appliquer
     `validate_new_password` à la **création de compte** (élève et professeur) et
     **brancher la réinitialisation** de mot de passe en réutilisant le cœur
     (`core.auth.reset`, table `auth_tokens`).
     Petit, à haute valeur, sans opt-in
     ni refonte.
     C'est le trou de sécurité de base le plus concret.

   - **T2 : MFA prof/admin (ensuite, ADR ultérieur).** Installer l'opt-in
     `forge-mvc-mfa`, migrer `auth_mfa_*`, brancher le flux TOTP + codes de secours
     au login pour les rôles `professeur`/`admin`.
     Se greffe sur le socle mot de
     passe de T1.
     Exigence du cadrage §20.

   - **T3 : Permissions fines (si/quand un besoin réel émerge).** Aligner
     `rbac.json` sur le cadrage §19 (permissions par action).
     **Non entrepris tant
     que la granularité admin/professeur suffit** : éviter la granularité
     spéculative (cohérent ADR-013, principe Forge « pas de couche avant besoin »).

3. **Réutiliser le cœur, ne rien réimplémenter.** Le flux de reset s'appuie sur
   les fonctions **pures** du cœur (`create_password_reset_token`,
   `reset_password_with_token`, `validate_new_password`) ; l'app ne fait que la
   **persistance** (`auth_tokens`, `users.password_hash`) en SQL visible et
   paramétré.
   Aucun token brut n'est stocké (seul le hash).

4. **Anti-énumération.** La demande de reset renvoie un message **générique**
   quel que soit l'existence du compte.
   En l'absence de mailer configuré, le lien
   de reset est affiché à l'écran **uniquement si le compte existe** (compromis de
   développement ; en production, l'envoi se fera par email).

## Conséquences

- **Positif** : la sécurité de base est documentée et reconnue ; le durcissement
  des mots de passe comble le manque le plus concret sans dépendance nouvelle ; la
  trajectoire MFA/permissions est tracée et séquencée.
  Réutilisation du cœur, pas
  de dette.
- **Négatif / limites** : la MFA (exigence du cadrage) reste différée à T2 ; les
  permissions restent grossières (T3 différé).
  Le reset sans mailer affiche le lien
  en dev, à remplacer par un envoi email en production.
- **Réversibilité** : chaque temps est isolé (contrôleur/routes dédiés).
  T1
  n'introduit aucune table (réutilise `auth_tokens`).

## Alternatives écartées

- **Commencer par la MFA.** Rejetée pour l'instant : gros morceau (opt-in + TOTP +
  UI + secours), dépendant de la maturité de `forge-mvc-mfa` (retour-006 F15).
  La
  MFA est une couche *supplémentaire* ; le durcissement mot de passe est un manque
  de *base* plus urgent.
  Reprogrammée en T2.
- **Affiner d'emblée les permissions (§19).** Rejetée : refonte de `rbac.json` +
  re-mapping des gardes, risque de régression, pour un gain théorique tant qu'il
  n'y a qu'admin/professeur.
  Granularité spéculative.
  Reprogrammée en T3 sur besoin.
- **Ouvrir la self-registration.** Rejetée : la création par l'admin est un choix
  pédagogique (comptes maîtrisés) ; pas de besoin d'auto-inscription.
