# Retour terrain 003 — `forge_migrations` absente après provisioning manuel de `db:init`

**Destinataire :** équipe Forge (dépôt `caucrogeGit/Forge`).
**Émetteur :** projet RéférenCiel Manager (banc d'essai, ADR-005).
**Statut :** à remonter.

## Environnement

- `forge-mvc` **e3197866**, `forge-mvc-mariadb` **ff41d83**, MariaDB active.
- Provisioning en **mode affiche** (défaut de `db:init`) : le SQL est exécuté à la
  main via `sudo mariadb`, conformément à ADR-067 (Forge ne demande jamais le root
  serveur) — cas normal quand `DB_ADMIN` n'a **pas** les droits serveur.

## Contexte

Chaîne du ticket 07 : après `make:entity` + `migration:make`, on lance
`forge migration:status` / `migration:apply`. Les deux échouent :

```
[ERREUR] Lecture de forge_migrations impossible. Lancez d'abord : forge db:init
```

Or `db:init` **a déjà été lancé** (base et comptes créés, `forge doctor` passe).

## Constat

### F9 — La table `forge_migrations` n'est pas créée par le chemin de provisioning manuel

- En **mode affiche** (défaut), `forge db:init` imprime `CREATE DATABASE` + deux
  comptes `CREATE OR REPLACE USER` + `FLUSH PRIVILEGES`, **mais pas** le
  `CREATE TABLE forge_migrations`.
- Le registre n'est créé qu'en **`--run`** (`cli/entities/db_init.py`,
  `_create_forge_migrations_table`, l.~244/367). Or `--run` suppose que
  `DB_ADMIN` a les **droits serveur** (CREATE DATABASE, CREATE USER) — ce qui
  **contredit** le compte admin *scellé à la base* que `db:init` recommande
  lui-même (`GRANT ALL ON \`DB_NAME\`.* TO admin`).
- Résultat : qui provisionne à la main (le cas sûr documenté) n'obtient **jamais**
  `forge_migrations`, et toutes les commandes `migration:*` échouent avec un
  message **trompeur** (« Lancez d'abord db:init » — déjà fait).

### Contournement appliqué

Création manuelle de `forge_migrations` avec la **DDL exacte** du framework
(`forge_mvc_mariadb.dialect.forge_migrations_ddl` /
`db_init.FORGE_MIGRATIONS_TABLE_SQL`), via le compte admin scellé (qui a `CREATE`
sur la base). `migration:status`/`apply` fonctionnent ensuite normalement.

## Proposition

1. **Inclure `CREATE TABLE forge_migrations` dans le SQL affiché** par `db:init`
   (mode affiche) : il ne requiert que des droits **sur `DB_NAME`**, que le compte
   admin scellé possède. Le provisioning manuel devient complet.
2. **Ou** rendre le registre auto-amorçable : `migration:apply` crée
   `forge_migrations` au premier passage (idempotent), au lieu de refuser.
3. **Corriger le message d'erreur** : distinguer « base non provisionnée » de
   « registre `forge_migrations` absent », et pointer le bon remède plutôt qu'un
   `db:init` déjà exécuté.

## Référence

Chaîne reproduite dans [docs/procedures](../procedures/montee-squelette-forge.md)
côté environnement ; entité de test : `AnneeScolaire` (ticket 07).
