# Retour terrain 012 : Deux défauts du moteur d'entités : faux positif `entity:validate` (FK) et split SQL cassé par une apostrophe en commentaire

**Destinataire :** équipe Forge (dépôt `caucrogeGit/Forge`).
**Émetteur :** projet RéférenCiel Manager (banc d'essai, ADR-006).
**Statut :** **F26 RÉSOLU** côté Forge (2026-07-12, sha `399db24f`), voir note sous F26.
F27 : à remonter.

## Environnement

- `forge-mvc` **32f552cc**, opt-in **`forge-mvc-entities` 32f552cc** (ADR-070 : moteur
  d'entités extrait du cœur), `forge-mvc-mariadb`, MariaDB, Python 3.12.
- Contexte : construction du pivot enrichi **`InscriptionEleve`** (3 `many_to_one`
  vers `Eleve`, `Classe`, `AnneeScolaire`) sur le **nouveau modèle FK** introduit avec
  la résolution de [retour-011](retour-011-make-relation-unicite-globale-noms-et-fk.md).

## Contexte

Le nouveau modèle est cohérent et correct en génération : `make:relation` déclare la
FK comme **champ `foreign_key`** du contrat d'entité, `sync:entity` en génère la
**colonne**, `sync:relations` la **contrainte + index**.
Deux défauts se glissent
néanmoins dans la chaîne : l'un dans la validation, l'autre à l'application.

## Constats

### F26 : `entity:validate` : faux positif `FORGE_RELATION_FK_COLLISION` sur un champ *de type* `foreign_key`

- **Symptôme** : après `make:relation` (qui ajoute lui-même le champ `foreign_key` à
  l'entité **et** la relation à `relations.json`), `entity:validate` échoue :

  ```text
  [ERREUR] Validation sémantique
    Code : FORGE_RELATION_FK_COLLISION
    Chemin  : $.relations[N].foreign_key
    Raison  : la clé étrangère "annee_scolaire_id" (relation annee_scolaire) collisionne
              avec un champ métier déclaré dans l'entité InscriptionEleve.
    Conseil : Déclarez explicitement foreign_key avec un nom différent.
  ```

- **Cause** (`forge_mvc_entities/entity_semantic_validate.py`, règle 7, ~l.211-228) :

  ```python
  existing_fields = { f.get("name", "") for f in from_entity.get("fields", []) ... }
  fk = relation.get("foreign_key") or f"{rel_name}_id"
  if fk in existing_fields:
      errors.append(SemanticError(code=FORGE_RELATION_FK_COLLISION, ...))
  ```

  `existing_fields` inclut **tous** les champs, **sans exclure ceux de `type:
  "foreign_key"`**.
  Or ce champ **est** la FK que la relation déclare : ce n'est pas un
  « champ métier » en collision.
  La règle vise à détecter un vrai conflit (une colonne
  métier homonyme d'une FK déduite), mais elle frappe le cas normal.

- **Incohérence interne** : `make:relation` **produit** exactement cet état (champ
  `foreign_key` + relation), la génération SQL est **correcte** (`sync:entity` →
  colonne, `sync:relations` → contrainte, sans doublon), et pourtant `entity:validate`
  le **rejette**.
  Un même Forge crée un état que son propre validateur refuse.

- **Impact** : `entity:validate` est **inutilisable** dès qu'une entité a une FK via le
  nouveau modèle (toute entité liée).
  Non bloquant pour `make check` (`project:check`
  n'exécute pas cette règle), mais casse une porte qualité que le projet utilisait.

- **Correctif proposé** : dans la règle 7, **exclure les champs `type == "foreign_key"`**
  de `existing_fields` (ou ne signaler la collision que si le champ homonyme est d'un
  **autre** type).
  Un champ `foreign_key` portant le nom de la FK est l'état **attendu**.

- **Confirmation (2026-07-11, Forge 1.0.0rc2 / `forge-mvc-entities` 1.0.0rc2)** : F26
  **persiste**.
  `forge entity:validate` remonte **54** occurrences
  `FORGE_RELATION_FK_COLLISION`, une par champ `foreign_key` du projet, sur toutes les
  entités liées (socle scolaire, référentiel, Bloc B).
  Chaque entité reste valide
  individuellement (`[OK]`) ; seules les **relations** sont rejetées.
  Schéma en base
  **sain** (une colonne + une contrainte par FK, vérifié sur `referentiel_niveau_classe`).
  `make check` / `forge project:check` restent **verts** (cette règle n'y est pas
  exécutée).
  Contrats projet **inchangés** (le pattern champ + relation est l'état
  officiel ADR-069).
  Constaté lors de la vérification des tickets 09–11.

- **RÉSOLU (2026-07-12, Forge sha `399db24f`)** : la règle 7 n'assimile plus un champ
  de type `foreign_key` à une collision.
  `forge entity:validate` remonte désormais
  **0 erreur** (44 fichiers valides) sur les contrats du projet, **inchangés**.
  Le
  correctif proposé ci-dessus a été appliqué côté framework.

### F27 : `split_sql_statements` : une apostrophe **dans un commentaire** casse le découpage des instructions

- **Symptôme** : `migration:apply` échoue avec une erreur de syntaxe MariaDB pointant
  la **2ᵉ** instruction, alors que chaque instruction est individuellement valide :

  ```text
  [ERREUR] ...create_inscription_eleve.sql: erreur SQL ... near
  'ALTER TABLE inscription_eleve ADD CONSTRAINT fk_inscription_eleve_classe_...' at line 10
  ```

- **Cause** (`forge_mvc_entities/db_apply.py`, `split_sql_statements`, ~l.173-192) : le
  découpage bascule un drapeau `in_single_quote` sur **chaque** caractère `'`, **sans
  tenir compte des commentaires** (`-- …`, `/* … */`) :

  ```python
  for char in sql:
      if char == "'":
          in_single_quote = not in_single_quote
      if char == ";" and not in_single_quote:
          ...  # découpe
  ```

  Un commentaire SQL contenant une apostrophe française (ici `n'inclut` dans un
  `-- commentaire`) ouvre un faux littéral : tous les `;` suivants sont considérés
  « dans une chaîne » et **ne découpent plus**.
  Les 4 `ALTER` sont alors envoyés en
  **une seule** requête multi-instructions → refus du serveur.

- **Impact** : toute migration (ou tout SQL exécuté via ce chemin) contenant, **en
  commentaire**, une **apostrophe** OU un **`;`** est cassée de façon **non évidente**
  (le message pointe une instruction valide).
  Le splitter n'est pas conscient des
  commentaires : un `;` en commentaire **découpe** au mauvais endroit, une `'` ouvre un
  faux littéral.
  Piège français (apostrophes) **et** piège de rédaction (un `;` dans un
  commentaire explicatif).
  *Confirmé deux fois sur le banc d'essai : `n'inclut` puis un
  `;` dans un commentaire de migration `create_scenario`.*

- **Contournement (projet)** : rédiger les commentaires de migration **sans apostrophe
  ni `;`** (ASCII sobre).
  Fragile et facile à oublier.

- **Correctif proposé** : rendre `split_sql_statements` **conscient des commentaires** :
  ignorer `-- …` jusqu'à la fin de ligne et `/* … */` avant de traiter `'` et `;`.
  Idéalement gérer aussi les guillemets doubles et les apostrophes échappées.

## Synthèse

Le nouveau modèle FK (retour-011 résolu) fonctionne et produit un CRUD FK-aware.
Restent
deux défauts en marge : une **porte qualité qui rejette l'état normal** (F26) et un
**découpeur SQL** trompé par une apostrophe en commentaire (F27).
Aucun ne bloque
`make check`, mais tous deux nuisent à une chaîne « qui tourne du premier coup ».

## Référence

`forge_mvc_entities/entity_semantic_validate.py` (règle 7, `FORGE_RELATION_FK_COLLISION`) ;
`forge_mvc_entities/db_apply.py` (`split_sql_statements`).
Preuves : sorties littérales
ci-dessus.
Flux : Bloc A, entité `InscriptionEleve` (migration `create_inscription_eleve`).
