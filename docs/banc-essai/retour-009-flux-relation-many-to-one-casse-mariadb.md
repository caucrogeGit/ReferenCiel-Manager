# Retour terrain 009 : Le flux `make:relation` (many_to_one) ne produit pas de schéma applicable sur MariaDB

**Destinataire :** équipe Forge (dépôt `caucrogeGit/Forge`).
**Émetteur :** projet RéférenCiel Manager (banc d'essai, ADR-006).
**Statut :** ✅ Résolu dans forge-mvc 809d224f (2026-07-08), vérifié sur le banc d'essai (table classe + FK créées).

## Environnement

- `forge-mvc` **f38d5159**, `forge-mvc-mariadb`, MariaDB.
- Reproduction : `make:entity Classe` (code, libelle) → `make:relation`
  (`Classe → AnneeScolaire`, `Classe → NiveauClasse`) → `sync:relations` →
  `sync:entity Classe`.

## Contexte

Bloc A : `Classe` référence `AnneeScolaire` et `NiveauClasse` (deux `many_to_one`).
Impossible d'obtenir une relation **appliquable** sur MariaDB sans écrire le SQL à
la main.
Trois défauts se cumulent.

## Constats

### F19 : La colonne FK n'est jamais générée

- `make:relation` n'écrit **que** dans `mvc/entities/relations.json`
  (`cli/entities/make_relation.py:4`).
  Il n'ajoute pas de champ FK au contrat de
  l'entité et ne génère aucune colonne.
- `generate_relations_sql` (`cli/entities/relations.py:198-208`) émet **uniquement**
  `ALTER TABLE ... ADD CONSTRAINT ... FOREIGN KEY (from_column) REFERENCES ...`,
  **jamais** `ADD COLUMN`.
- Résultat : `relations.sql` pose une contrainte sur `annee_scolaire_id`, colonne
  qui **n'existe nulle part** (ni `classe.json`, ni `classe.sql`, ni `classe_base.py`).

### F20 : Incohérence de nommage : colonne PascalCase vs FK snake_case

En ajoutant la FK comme champ (`annee_scolaire_id`, `big_integer`) pour contourner
F19, `sync:entity` génère la colonne **`AnneeScolaireId`** (convention PascalCase des
colonnes), alors que `relations.sql` référence **`annee_scolaire_id`** (snake_case,
depuis `relations.json.foreign_key`).
La contrainte vise donc une colonne inexistante.

### F21 : Type FK incompatible : `BIGINT` vs `BIGINT UNSIGNED`

Un champ `big_integer` génère `BIGINT` (**signé**), mais la clé primaire visée est
`Id BIGINT UNSIGNED`.
MariaDB **refuse** une FK entre types différents
(`errno 150 / incompatible types`).

## Synthèse

Le trio rend `make:relation` **inutilisable de bout en bout** sur MariaDB : la
relation est déclarée, la contrainte est générée, mais aucune colonne compatible
n'est créée.
`make check` reste vert (les JSON sont valides) : le blocage n'apparaît
qu'à l'**application** du schéma.

## Proposition

1. **Générer la colonne FK** : `make:relation` (ou `sync:relations`) ajoute la
   colonne `<fk>` à l'entité source, avec le **bon type** (`BIGINT UNSIGNED` pour
   référencer un `Id BIGINT UNSIGNED`) et un `ADD COLUMN` dans `relations.sql` si la
   colonne n'existe pas.
2. **Cohérence de nommage** : aligner le nom de colonne FK (contrainte) sur la
   convention de colonnes de l'entité (Pascal vs snake) : un seul et même nom.
3. Idéalement, **intégrer la FK au contrat/CRUD** : le champ FK apparaît dans le
   modèle et le CRUD (sélection de l'entité liée), pas seulement comme contrainte.

## Contournement

Aucun propre côté projet : il faudrait écrire la migration `classe` à la main
(colonnes `annee_scolaire_id`/`niveau_classe_id` en `BIGINT UNSIGNED` + contraintes),
mais le CRUD généré (depuis `classe.json`) ne gérerait toujours pas les FK.
**Classe
est mise en pause** en attendant un correctif du flux relation.

## Référence

`cli/entities/relations.py:198`, `cli/entities/make_relation.py`.
Preuves : `classe.sql`
(`AnneeScolaireId BIGINT`), `relations.sql` (`FOREIGN KEY (annee_scolaire_id)`),
`annee_scolaire.sql` (`Id BIGINT UNSIGNED`).
Flux : ticket 07 (Bloc A, entité Classe).
