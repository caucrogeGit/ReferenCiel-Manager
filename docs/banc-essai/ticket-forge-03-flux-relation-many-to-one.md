# Ticket Forge 03 — Flux `make:relation` (many_to_one) inapplicable sur MariaDB

**Pour :** l'agent Claude Code travaillant sur le framework Forge (`caucrogeGit/Forge`).
**De :** projet RéférenCiel Manager, application-banc d'essai (ADR-005).
**Objet :** le flux relation `many_to_one` ne produit pas un schéma **applicable**
sur MariaDB — découvert en construisant l'entité `Classe` (FK vers `AnneeScolaire`
et `NiveauClasse`).

## Environnement

- `forge-mvc` **`f38d5159294ab246b1fd77a2615b4c96a3b64db1`**, `forge-mvc-mariadb`.
- Repro : `make:entity Classe` (code, libelle) → `make:relation` ×2 →
  `sync:relations` → `sync:entity Classe` → (impossible d'appliquer).

## P1 — Bloquant

### FORGE-12 · La colonne FK n'est jamais générée

- **Preuve** : `make:relation` n'écrit que dans `relations.json`
  (`cli/entities/make_relation.py:4`) ; `generate_relations_sql`
  (`cli/entities/relations.py:198-208`) émet seulement
  `ALTER TABLE ... ADD CONSTRAINT ... FOREIGN KEY (col) REFERENCES ...`,
  **jamais** `ADD COLUMN`. La colonne `annee_scolaire_id` n'existe donc nulle part
  (ni contrat, ni `classe.sql`, ni modèle).
- **Correctif** : générer la colonne FK (dans l'entité source et/ou un `ADD COLUMN`
  dans `relations.sql`), au bon type.

### FORGE-13 · Nom de colonne incohérent : PascalCase (entité) vs snake_case (contrainte)

- **Preuve** : en ajoutant la FK comme champ, `sync:entity` produit la colonne
  `AnneeScolaireId` (convention PascalCase des colonnes), tandis que `relations.sql`
  référence `annee_scolaire_id` → contrainte sur colonne inexistante.
- **Correctif** : un seul nom de colonne FK, cohérent entre l'entité et la contrainte.

### FORGE-14 · Type FK incompatible : `BIGINT` vs `BIGINT UNSIGNED`

- **Preuve** : champ `big_integer` → `BIGINT` (signé) ; PK visée `Id BIGINT UNSIGNED`
  → MariaDB refuse la FK (types incompatibles, errno 150).
- **Correctif** : les colonnes FK doivent adopter le type exact de la PK visée
  (`BIGINT UNSIGNED`).

## Point important (comme le ticket 02)

`make check` (pyright, ruff, pytest, `project:check`) est **vert** — les JSON de
relation sont valides. Le blocage n'apparaît qu'à l'**application** du schéma sur
un vrai MariaDB. Encore un cas que seul un parcours end-to-end révèle.

## Objectif

Rendre `make:entity` + `make:relation` + `migration:*` capables de produire une
relation `many_to_one` **appliquable et gérée par le CRUD** sur MariaDB, sans SQL
manuel. Idéalement, la FK apparaît aussi dans le modèle/CRUD (sélection de l'entité
liée), pas seulement comme contrainte.

## Référence

`retour-009`. Preuves : `cli/entities/relations.py:198`, `cli/entities/make_relation.py`,
`classe.sql`, `relations.sql`, `annee_scolaire.sql`. Flux : Bloc A, entité `Classe`.
