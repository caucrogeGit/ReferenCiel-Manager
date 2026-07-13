# Ticket Forge 04 : Intégrer les relations à `migration:make` et au CRUD

**Pour :** l'agent Claude Code travaillant sur le framework Forge (`caucrogeGit/Forge`).
**De :** projet RéférenCiel Manager, application-banc d'essai (ADR-006).
**Objet :** après le correctif du **schéma** des relations (ticket-03 résolu,
`809d224f`), la **chaîne applicative** ne relie toujours pas les relations à la
migration ni au CRUD, découvert sur l'entité `Classe`.

## Environnement

- `forge-mvc` **`809d224fa4b77daffab5ac5edbe6d326ec085c67`**, `forge-mvc-mariadb`.
- Repro : `make:entity Classe` → `make:relation` ×2 → `sync:relations` →
  `migration:make create_classe --from-entity Classe` → `make:crud Classe`.

## P2 : Chaîne applicative incomplète

### FORGE-15 · `migration:make` n'intègre pas `relations.sql`

- **Preuve** : `--from-entity`/`--from-entities` ne produisent que les `CREATE TABLE`
  des entités ; le SQL de relations (`ADD COLUMN` + `FOREIGN KEY` + `INDEX`) de
  `mvc/entities/relations.sql` est ignoré. Il faut l'**ajouter à la main** à la
  migration.
- **Correctif** : option `--with-relations` (ou inclure les relations concernées dans
  `--from-entity`/`--from-entities`), dans l'ordre tables → contraintes.

### FORGE-16 · `make:crud` ignore les relations (formulaire sans entité liée)

- **Preuve** : `make:crud` lit `<e>.json` mais pas `relations.json`. Les FK
  (`annee_scolaire_id`, `niveau_classe_id`, `NOT NULL`) n'apparaissent ni dans le
  formulaire, ni dans le modèle, ni dans la fiche/liste → **création impossible via
  l'UI** (INSERT sans les FK requises). Seule la liste fonctionne.
- **Correctif** : `make:crud` **conscient des relations** : pour chaque FK, un
  `<select>` peuplé depuis l'entité liée (via `name`/`inverse_name`), inclus dans le
  formulaire + le modèle (INSERT/UPDATE) ; en affichage, montrer le libellé lié
  plutôt que l'`id`.

## Objectif

Rendre la chaîne `make:entity → make:relation → migration → make:crud` **complète et
fonctionnelle pour une entité avec relations** : table + FK créées **et** CRUD
utilisable (création avec choix de l'entité liée), sans SQL manuel.

## Référence

`retour-010`.
Preuves : options de `migration:make` ; générateurs CRUD
(`cli/entities/crud/*`) lisant `<e>.json` sans `relations.json`.
Flux : Bloc A,
entité `Classe` (schéma OK depuis ticket-03).
