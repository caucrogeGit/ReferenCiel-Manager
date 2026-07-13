# Retour terrain 010 — Les relations ne sont pas intégrées à `migration:make` ni au CRUD généré

**Destinataire :** équipe Forge (dépôt `caucrogeGit/Forge`).
**Émetteur :** projet RéférenCiel Manager (banc d'essai, ADR-006).
**Statut :** à remonter.

## Environnement

- `forge-mvc` **809d224f** (le flux relation génère désormais un SQL correct —
  [retour-009](retour-009-flux-relation-many-to-one-casse-mariadb.md) résolu),
  `forge-mvc-mariadb`, MariaDB.
- Contexte : entité `Classe` avec deux `many_to_one` (`AnneeScolaire`, `NiveauClasse`).

## Contexte

Une fois le **schéma** des relations correct (retour-009 résolu), deux **maillons de
la chaîne** restent non reliés aux relations : la **migration** et le **CRUD**.

## Constats

### F22 — `migration:make` n'intègre pas `relations.sql`

- **Symptôme** : aucune option de `migration:make` ne produit le SQL des relations.
  `--from-entity <E>` et `--from-entities` ne couvrent que les `CREATE TABLE` des
  entités ; `relations.sql` (les `ADD COLUMN` / `FOREIGN KEY` / `INDEX`) est ignoré.
- **Conséquence** : pour créer une table **avec ses FK**, il faut **ajouter à la
  main** le contenu de `mvc/entities/relations.sql` dans le fichier de migration
  (après le `CREATE TABLE`).
- **Correctif proposé** : une option `--with-relations` / `--from-relations`, **ou**
  que `--from-entity`/`--from-entities` incluent le SQL de relations concerné (dans
  l'ordre : tables puis contraintes).

### F23 — Le CRUD généré ne gère pas les champs FK (formulaire sans entité liée)

- **Symptôme** : `make:crud <E>` lit `<e>.json` (champs propres) mais **pas**
  `relations.json`. Le contrôleur, le modèle et le formulaire générés **ignorent**
  les colonnes FK (`annee_scolaire_id`, `niveau_classe_id`).
- **Conséquence** : le **formulaire de création n'a aucun champ** pour l'année/le
  niveau ; or ces FK sont `NOT NULL` → **impossible de créer une `Classe` via l'UI**
  (l'INSERT échouerait). Seule la **liste** fonctionne.
- **Correctif proposé** : rendre `make:crud` **conscient des relations** — lire
  `relations.json`, générer pour chaque FK un champ **`<select>`** peuplé depuis
  l'entité liée (via son `name`/`inverse_name`), et l'inclure dans le formulaire, le
  modèle (INSERT/UPDATE) et l'affichage (fiche/liste : montrer le libellé lié, pas
  l'`id`).

## Synthèse

Le **schéma** des relations est correct (retour-009), mais la **chaîne applicative**
s'arrête là : ni la migration ni le CRUD ne « voient » les relations. Pour une entité
liée, il faut compléter la migration à la main et le CRUD reste inutilisable en
création. Combler F22/F23 rendrait la chaîne `make:entity → make:relation →
migration → make:crud` **complète pour une entité avec relations**.

## Contournement (projet)

- Migration : SQL de `relations.sql` **copié dans la migration** `create_classe`.
- CRUD : utilisé en **lecture** (liste) ; création de `Classe` faite par **SQL direct**
  (seed) en attendant un CRUD conscient des FK.

## Référence

`cli/entities/migration_make` (options `--from-*`), `cli/entities/crud/*` (lecture de
`<e>.json` sans `relations.json`). Flux : Bloc A, entité `Classe`
([journal §5.5](../journal-de-progression.md)).
