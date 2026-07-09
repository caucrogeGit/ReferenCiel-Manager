# Retour terrain 013 — Le pivot `many_to_many` généré type ses colonnes en `INT` (FK incompatible avec `BIGINT UNSIGNED`)

**Destinataire :** équipe Forge (dépôt `caucrogeGit/Forge`).
**Émetteur :** projet RéférenCiel Manager (banc d'essai, ADR-005).
**Statut :** à remonter.

## Environnement

- `forge-mvc` **32f552cc**, opt-in `forge-mvc-entities` **32f552cc**, `forge-mvc-mariadb`,
  MariaDB, Python 3.12.
- Contexte : Bloc A, entité **`Groupe`** avec une relation **`many_to_many`** vers
  `Eleve` (pivot `groupe_eleve`, jonction pure) créée par `make:relation`.

## Contexte

`make:relation` (type `many_to_many`) écrit un bloc `pivot` correct dans
`relations.json` :

```json
"pivot": {
  "table": "groupe_eleve", "from_key": "groupe_id", "to_key": "eleve_id",
  "id": true, "unique_pair": true, "on_delete": "cascade", "fields": []
}
```

Mais le SQL que `sync:relations` en dérive **ne s'applique pas** sur MariaDB.

## Constat

### F28 — Colonnes du pivot en `INT` au lieu de `BIGINT UNSIGNED` (+ `ENGINE` manquant)

- **Symptôme** : le `CREATE TABLE` du pivot généré dans `mvc/entities/relations.sql` :

  ```sql
  CREATE TABLE IF NOT EXISTS groupe_eleve (
      id INT NOT NULL AUTO_INCREMENT,
      groupe_id INT NOT NULL,
      eleve_id INT NOT NULL,
      PRIMARY KEY (id),
      UNIQUE KEY uq_groupe_eleve (groupe_id, eleve_id),
      INDEX idx_groupe_eleve_groupe_id (groupe_id),
      INDEX idx_groupe_eleve_eleve_id (eleve_id),
      CONSTRAINT fk_groupe_eleve_groupe_id
          FOREIGN KEY (groupe_id) REFERENCES groupe (id) ON DELETE CASCADE,
      CONSTRAINT fk_groupe_eleve_eleve_id
          FOREIGN KEY (eleve_id) REFERENCES eleve (id) ON DELETE CASCADE
  );
  ```

- **Défauts** :
  1. **Type incompatible** : `groupe_id` / `eleve_id` sont `INT`, mais les PK visées
     (`groupe.Id`, `eleve.Id`) sont **`BIGINT UNSIGNED`**. MariaDB **refuse** la FK
     (`errno 150 / incompatible types`) — exactement le défaut **F21** de
     [retour-009](retour-009-flux-relation-many-to-one-casse-mariadb.md), corrigé pour
     le `ADD COLUMN` du `many_to_one` mais **non répercuté** au générateur de pivot.
  2. **`ENGINE` / `CHARSET` absents** : le `CREATE TABLE` pivot ne porte pas
     `ENGINE=InnoDB DEFAULT CHARSET=utf8mb4` (contrairement aux tables d'entités) —
     incohérence de moteur/charset possible.
  3. **Casse de la PK référencée** : `REFERENCES groupe (id)` (minuscule) alors que la
     colonne est `Id`. Sans effet sur MariaDB (noms de colonnes insensibles à la casse),
     mais incohérent avec le reste du SQL généré.

- **Impact** : toute relation `many_to_many` est **inapplicable telle quelle** ; il faut
  réécrire le `CREATE TABLE` du pivot à la main (types `BIGINT UNSIGNED`, `ENGINE`).

- **Correctif proposé** : aligner le générateur de pivot sur la convention des PK —
  colonnes `id` / `from_key` / `to_key` en **`BIGINT UNSIGNED`**, ajouter la clause
  `ENGINE=InnoDB DEFAULT CHARSET=utf8mb4`, et référencer `Id` avec la bonne casse.
  Idéalement, **réutiliser le même chemin de génération** que les colonnes FK
  `many_to_one` (déjà corrigées en F21) pour éviter la divergence.

## Contournement (projet)

`CREATE TABLE groupe_eleve` **réécrit à la main** dans la migration `create_groupe`
(colonnes `BIGINT UNSIGNED`, `ENGINE` ajouté, `REFERENCES … (Id)`). La table pivot
s'applique alors sans erreur.

## Référence

Générateur de SQL de relations (bloc pivot `many_to_many`) dans `forge-mvc-entities`
(`relations.py` / génération `sync:relations`). Preuve : `mvc/entities/relations.sql`
(table `groupe_eleve`, colonnes `INT`). Contournement : migration `create_groupe`.
Flux : Bloc A, entité `Groupe`.
