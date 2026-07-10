# Banc d'essai — retours terrain vers Forge

RéférenCiel Manager sert de **banc d'essai** au framework Forge (ADR-005). Cette
rubrique consigne les **retours terrain** issus de l'usage réel : écarts,
frictions et suggestions, destinés à l'équipe qui maintient Forge.

Chaque retour est **fondé sur des preuves reproductibles** (commande + sortie) et
distingue clairement :

- **Défaut** — le squelette ou l'outil s'écarte d'un standard que Forge s'impose ;
- **Suggestion** — amélioration proposée, en tenant compte des choix de Forge
  (ex. squelette volontairement minimal, ADR-024) ;
- **À vérifier** — hypothèse à confirmer par un test.

On **révèle avant de corriger** (charte Forge, règle B) : on ne contourne pas en
silence, on documente et on remonte.

## Retours

| # | Sujet | Statut |
| --- | --- | --- |
| [001](retour-001-conformite-squelette.md) | Conformité du squelette `forge new` aux standards Forge (typage strict, config qualité, doc, tests) | ✅ Résolu (f38d5159) |
| [002](retour-002-commande-skeleton-upgrade.md) | Commande de montée de squelette d'un projet existant (`forge skeleton:upgrade`) | ✅ Résolu (f38d5159) |
| [003](retour-003-forge-migrations-provisioning-manuel.md) | `forge_migrations` absente après provisioning manuel de `db:init` (message trompeur) | ✅ Résolu (f38d5159) |
| [004](retour-004-code-genere-non-conforme-portes-qualite.md) | Le code généré ne passe pas les portes qualité (pyright strict, ruff) | ✅ Résolu (f38d5159) |
| [005](retour-005-make-crud-code-casse-et-non-conforme.md) | `make:crud` génère du code cassé (helper flash manquant) et non conforme (modèle non typé) | ✅ Résolu (f38d5159) |
| [006](retour-006-db-apply-ignore-models-sql-et-socle-auth-rbac.md) | `db:apply` ignore `mvc/models/sql/` ; `auth:init` génère un socle à dépendances RBAC/MFA non satisfaites | ✅ Résolu (f38d5159) |
| [007](retour-007-aucune-page-login-scaffoldee.md) | Aucune page de login fournie ni scaffoldée, alors que le cœur redirige vers `/login` | ✅ Résolu (f38d5159) |
| [008](retour-008-bugs-runtime-login-mariadb-et-bouton-crud.md) | Deux bugs runtime du code généré (login MariaDB `is_active`, composant bouton CRUD manquant) | ⚠️ F17 résolu (809d224f) · F18 en attente |
| [009](retour-009-flux-relation-many-to-one-casse-mariadb.md) | Flux `make:relation` (many_to_one) inapplicable sur MariaDB (colonne FK non générée, nom Pascal/snake, type `BIGINT` vs `UNSIGNED`) | ✅ Résolu (809d224f) |
| [010](retour-010-relations-non-integrees-migration-et-crud.md) | Relations non intégrées à `migration:make` ni au CRUD généré (FK absentes du formulaire) | À remonter |
| [011](retour-011-make-relation-unicite-globale-noms-et-fk.md) | `make:relation` impose une unicité **globale** du nom de relation (F24) et de la colonne FK (F25) — schémas multi-pivots inexprimables avec des noms fidèles au dictionnaire | ✅ Résolu (32f552cc) |
| [012](retour-012-entity-validate-faux-positif-fk-et-split-sql-apostrophe.md) | Faux positif `entity:validate` sur un champ `foreign_key` (F26) ; `split_sql_statements` cassé par une apostrophe en commentaire (F27) | À remonter |
| [013](retour-013-pivot-many-to-many-colonnes-int-au-lieu-de-bigint-unsigned.md) | Le pivot `many_to_many` généré type ses colonnes en `INT` au lieu de `BIGINT UNSIGNED` → FK errno 150 (+ `ENGINE` manquant) (F28) | À remonter |
| [014](retour-014-forge-mvc-admin-snake-case-vs-entities-pascalcase.md) | `forge-mvc-admin` exige des champs snake_case, incompatibles avec les colonnes PascalCase de `forge-mvc-entities` (colonnes multi-mots inutilisables) (F29) | À remonter |
| [015](retour-015-rbac-resolveur-session-depreciee-et-schema-non-livre.md) | `forge-mvc-rbac` : resolveur adossé à une session **dépréciée** (rôles toujours vides sur l'auth moderne, F30) ; aucun schéma SQL ni `rbac:sync` livrés (F31) ; deux modèles de permission disjoints (F32) | À remonter |
| [016](retour-016-sessions-db-hors-catalogue-schema-non-livre-et-read-modify-write-non-transactionnel.md) | `forge-mvc-sessions-db` : opt-in du monorepo **hors catalogue** `opt-in:list` (F33) ; table non provisionnée, docstring vers un `.sql` fantôme, DDL mono-backend (F34) ; `cleanup_expired()` sans planificateur, `jobs` ≠ cron (F35) ; **read-modify-write non transactionnel** → « atomique » non tenu, course dès le serveur threadé (F36) ; horodatages heure locale + double horloge (F37) ; warning squelette vers un ADR de session inexistant (F38) | **Résolu** (Forge `5dbb382`, 6/6) |
| [017](retour-017-sessions-gc-namorce-pas-la-config-et-help-sexecute.md) | `forge sessions:gc` n'amorce pas la config projet (`env/dev`) → `Access denied`, inutilisable en cron (F39) ; `--help` sans garde générique dans `dispatch_optin` — filet générique dans `dispatch_optin` (F40) | **Résolu** (Forge `2f2386a`, ADR-072) |
