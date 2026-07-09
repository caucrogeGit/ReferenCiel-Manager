# Retour terrain 011 — `make:relation` impose une unicité **globale** du nom de relation et de la colonne FK (schémas multi-pivots inexprimables)

**Destinataire :** équipe Forge (dépôt `caucrogeGit/Forge`).
**Émetteur :** projet RéférenCiel Manager (banc d'essai, ADR-005).
**Statut :** ✅ **Résolu dans forge-mvc 32f552cc** (2026-07-09) — **vérifié bout-en-bout** sur le banc d'essai.

> **Correctif vérifié.** Sur `32f552cc`, `make:relation InscriptionEleve → AnneeScolaire`
> accepte le nom **`annee_scolaire`** et la colonne **`annee_scolaire_id`** — pourtant
> déjà portés par `Classe` — sans erreur. L'unicité est désormais **scopée par entité
> source**. Bonus structurel (réponse aussi à [retour-009](retour-009-flux-relation-many-to-one-casse-mariadb.md)/[010](retour-010-relations-non-integrees-migration-et-crud.md)) :
> `make:relation` déclare la FK comme **champ `foreign_key`** du contrat d'entité
> (`{"type": "foreign_key", "references": "AnneeScolaire"}`), si bien que `sync:entity`
> génère la **colonne** (dans le `CREATE TABLE`) et `sync:relations` la **contrainte +
> index** (sans dupliquer la colonne). La table `inscription_eleve` a été créée et son
> CRUD généré est **FK-aware** (voir [retour-012](retour-012-entity-validate-faux-positif-fk-et-split-sql-apostrophe.md)
> pour deux défauts résiduels rencontrés au passage).

## Environnement

- `forge-mvc` **809d224f** (le flux relation génère un SQL correct depuis
  [retour-009](retour-009-flux-relation-many-to-one-casse-mariadb.md)),
  `forge-mvc-mariadb`, MariaDB, Python 3.12.
- Contexte : Bloc A, entité **`InscriptionEleve`** (pivot enrichi) portant **trois**
  `many_to_one` vers `Eleve`, `Classe` et `AnneeScolaire`.

## Contexte — ce que révèle le deuxième pivot

`Classe` (premier pivot) référence déjà `AnneeScolaire` (relation `annee_scolaire`,
FK `annee_scolaire_id`). En construisant `InscriptionEleve`, qui référence **aussi**
`AnneeScolaire` **et** `Classe`, `make:relation` **refuse** ces relations : il traite
le **nom de relation** et le **nom de colonne FK** comme des identifiants **globaux**
sur tout `relations.json`, au lieu de les scoper à l'**entité source**.

Les deux premières relations d'`InscriptionEleve` (`eleve` / `eleve_id`,
`classe` / `classe_id`) passent — non par correction, mais **par chance** : aucun de
ces noms n'était encore pris. Le blocage tombe dès qu'un nom entre en collision.

## Constats

### F24 — Le **nom de relation** est un espace de noms global (devrait être par entité source)

- **Symptôme** : créer `InscriptionEleve → AnneeScolaire` avec le nom naturel
  `annee_scolaire` échoue.
- **Preuve** (sortie littérale) :

  ```text
  Nom de la relation [annee_scolaire] : annee_scolaire
  ...
  [ERREUR] .../mvc/entities/relations.json: une relation nommée 'annee_scolaire' existe déjà
  ```

- **Analyse** : le `name` d'une relation est l'**accesseur côté source**
  (`InscriptionEleve.annee_scolaire`). Il n'entre pas en conflit avec
  `Classe.annee_scolaire` : ce sont deux accesseurs sur **deux entités différentes**.
  L'unicité devrait porter sur le **couple `(from, name)`**, pas sur `name` seul.

### F25 — Le **nom de colonne FK** est un espace de noms global (devrait être par table source)

- **Symptôme** : en qualifiant le nom de relation pour contourner F24
  (`inscription_annee_scolaire`) tout en gardant la **colonne fidèle au dictionnaire**
  (`annee_scolaire_id`), l'écriture échoue encore.
- **Preuve** (sortie littérale) :

  ```text
  Nom de la relation [annee_scolaire] : inscription_annee_scolaire
  Colonne clé étrangère [inscription_annee_scolaire_id] : annee_scolaire_id
  ...
  [ERREUR] .../mvc/entities/relations.json: une clé étrangère nommée 'annee_scolaire_id' existe déjà
  ```

- **Analyse** : un `foreign_key` est une **colonne d'une table** ; son espace de noms
  est **la table**, pas la base entière. `inscription_eleve.annee_scolaire_id` et
  `classe.annee_scolaire_id` sont **deux colonnes distinctes de deux tables
  distinctes** — un schéma relationnel parfaitement valide (chaque table a sa FK vers
  `annee_scolaire`). L'unicité devrait porter sur `(from, foreign_key)`, pas sur
  `foreign_key` seul.

## Impact

Bloquant pour tout modèle réaliste : dès qu'**au moins deux entités référencent la
même cible** — cas standard des **tables pivots** (`InscriptionEleve` et
`AffectationProfesseurClasse` pointent toutes deux vers `AnneeScolaire` et `Classe`) —
il devient **impossible** d'exprimer les relations avec des noms de colonnes fidèles
au dictionnaire. On est forcé d'inventer des noms artificiels
(`inscription_annee_scolaire_id`), qui **divergent du modèle de données** et
alourdissent le SQL, les modèles et le CRUD à venir.

## À vérifier (côté Forge)

La sur-restriction est-elle **seulement dans le garde-fou interactif** de
`make:relation`, ou **aussi dans le validateur partagé** (`entity:validate`,
`sync:relations`, `project:check`) ?

- Si **seul le prompt** sur-restreint : une relation écrite **directement** dans
  `relations.json` (colonnes fidèles au dico) devrait passer `sync:relations` +
  `make check` → correctif ciblé sur le garde-fou.
- Si **le validateur aussi** : le contournement doit renommer les colonnes → correctif
  plus profond (scoper l'unicité par entité/table source dans le schéma de validation).

*(Non testé côté projet pour ne pas modifier `relations.json` sans décision ; à
trancher avec le correctif.)*

## Proposition

1. **Scoper l'unicité du `name`** au couple `(from, name)` — un accesseur est propre à
   son entité source.
2. **Scoper l'unicité du `foreign_key`** au couple `(from, foreign_key)` — une colonne
   n'a besoin d'être unique que **dans sa table**.
3. Conserver un contrôle global **uniquement** là où il a un sens réel (p. ex. unicité
   de `inverse_name` **sur l'entité cible**, si c'est une contrainte voulue).
4. Messages d'erreur qualifiés par la source : « une relation nommée 'annee_scolaire'
   existe déjà **sur InscriptionEleve** » plutôt qu'un message global trompeur (ici, la
   collision venait de `Classe`, invisible dans le message).

## Contournement (projet)

En attente de décision (cf. « À vérifier ») :

- **soit** on garde les colonnes fidèles au dictionnaire (`annee_scolaire_id`,
  `classe_id`, …) si le validateur les accepte en écriture directe ;
- **soit** on qualifie noms **et** colonnes FK par la source
  (`inscription_annee_scolaire_id`), au prix d'une divergence avec le dictionnaire.

`InscriptionEleve` est **en pause** : deux relations déclarées (`eleve_id`,
`classe_id`), la troisième (`annee_scolaire_id`) bloquée par F25.

## Référence

Garde-fou de `make:relation` (contrôle d'unicité sur `relations.json`) :
`cli/entities/make_relation.py`, `cli/entities/relations.py` (validation). Preuves :
les deux sorties littérales ci-dessus. Contrat concerné : `mvc/entities/relations.json`
(relations `Classe → AnneeScolaire` et `InscriptionEleve → …`). Flux : ticket 07
(Bloc A, entité `InscriptionEleve`).
