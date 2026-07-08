# Retour terrain 006 — `db:apply` ignore `mvc/models/sql/`, et `auth:init` génère un socle à dépendances non satisfaites

**Destinataire :** équipe Forge (dépôt `caucrogeGit/Forge`).
**Émetteur :** projet RéférenCiel Manager (banc d'essai, ADR-005).
**Statut :** ✅ Résolu dans forge-mvc f38d5159 (2026-07-08) — vérifié sur le banc d'essai.

## Environnement

- `forge-mvc` **e3197866**, `forge-mvc-mariadb`, MariaDB.
- Opt-ins **rbac** et **mfa** non installés (différés, garde-fou du projet).

## Contexte

Ticket 07 : mise en place du socle auth. `forge auth:init` génère 7 fichiers SQL
dans `mvc/models/sql/` et affiche :

```
[INFO] Commande suivante :
[INFO]   forge db:apply  # pour créer les tables Auth/User optionnelles
```

## Constats

### F14 — `db:apply` n'applique pas `mvc/models/sql/` (recommandation trompeuse)

`forge db:apply` ne collecte le SQL que dans **`mvc/entities/`**
(`cli/entities/db_apply.py`, `collect_sql_files` : itère `mvc/entities/*/` +
`relations.sql`). Le répertoire `mvc/models/sql/` — **où `auth:init` écrit** — est
**ignoré**. Lancer `db:apply` comme recommandé ne crée donc **aucune** table auth
(il ré-applique seulement les entités, `CREATE TABLE IF NOT EXISTS`).

**Proposition** : que `db:apply` applique aussi `mvc/models/sql/*.sql`, ou fournir
une commande dédiée (`forge auth:apply` ?). À défaut, corriger le message de
`auth:init` (il pointe une commande sans effet sur son propre output).

### F15 — `auth:init` génère le pont RBAC/MFA même sans les opt-ins → socle inapplicable tel quel

`auth:init` génère `user_roles.sql` avec une clé étrangère :

```sql
CONSTRAINT fk_user_roles_role_id FOREIGN KEY (role_id) REFERENCES roles(id)
```

Or la table `roles` appartient à l'**opt-in rbac** (non installé). Appliquer le
socle **complet** échoue (FK vers table absente). De même, `auth_mfa_*` relèvent
de l'opt-in **mfa**. `auth:status`/`auth:doctor` confirment : `forge_mvc_rbac` et
`forge_mvc_mfa` non importables.

**Proposition** : n'émettre `user_roles.sql` / `auth_mfa_*.sql` que si les opt-ins
correspondants sont présents (ou le signaler clairement), pour que le socle de
base soit **applicable en une fois**.

## Contournement appliqué

Migration versionnée `create_auth_socle` (via `migration:make` + remplissage
manuel) avec **les 4 tables de base** : `users`, `auth_tokens`, `auth_audit_log`,
`auth_rate_limit_attempts`. `user_roles` (RBAC) et `auth_mfa_*` (MFA) **omis**
(différés). Appliquée par `migration:apply` — tables créées, `auth:status` vert
sur le socle de base.

## Référence

Migration : `mvc/migrations/20260707163553_create_auth_socle.sql`. Entité/flux :
ticket 07. Voir aussi [retour-003](retour-003-forge-migrations-provisioning-manuel.md)
(autre friction du chemin base de données).
