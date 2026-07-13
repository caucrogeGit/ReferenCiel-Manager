# Retour terrain 020 — `forge-mvc-fixtures` : références inter-fixtures, ordre de chargement et scénario cohérent

**Destinataire :** équipe Forge (dépôt `caucrogeGit/Forge`).
**Émetteur :** projet RéférenCiel Manager (banc d'essai, ADR-006).
**Statut :** F43–F52 **RÉSOLUS** (`b2463149` → `38501db6`). Cycle
`fixtures:purge --run && fixtures:load --run` **idempotent** (≥ 2 cycles verts, callable
multi-tables `referentiel.py` inclus). La bascule est **complète** : `tools/seed_demo.py`
retiré, `mvc/fixtures/` fait foi.
d'un callable multi-tables (voir fin de document).

## Environnement

- `forge-mvc-fixtures` **1.0.0rc2** (opt-in outil CLI : `fixtures:make-factory`,
  `fixtures:generate`, `fixtures:load`, `fixtures:purge`), `forge-mvc-mariadb`,
  MariaDB, Python 3.12, Faker 39.

## Contexte / objectif

Le projet a un seed de **démonstration** maison (`tools/seed_demo.py`) : un
**parcours métier cohérent et déterministe** — comptes connus (`admin1234`,
`prof1234`, `eleve1234`) liés à leurs fiches, classe `2TNE-A`, élèves inscrits,
référentiel `ciel-2tne` importé, progression → évaluations sur **critères réels** →
**bilan calculé**. Objectif « 100 % Forge » : le remplacer par des fixtures natives.

**Constat** : `forge-mvc-fixtures` produit aujourd'hui du **volume aléatoire par
entité**, mais ne permet pas de bâtir un **jeu de données cohérent et relié**. Trois
manques bloquent le remplacement.

## Constats

### F43 — Pas de **références inter-fixtures** : les FK sont aléatoires

- **Symptôme** : `fixtures:make-factory eleve` puis `fixtures:generate eleve` produit
  ```sql
  INSERT INTO eleve (nom, prenom, identifiant, date_naissance, user_id)
  VALUES ('Lucas', 'Hélène', 'beau', '1984-06-02', 507);
  ```
  `user_id = 507` pointe un compte `users` **inexistant** → violation d'intégrité (ou
  rattachement au hasard). Le provider deviné pour une **clé étrangère** est
  `random_int(0, 1000)`.

- **Cause** : `Factory.definition()` génère **chaque entité indépendamment** ; il
  n'existe aucun moyen, dans une factory, de **référencer** une ligne créée par une
  autre fixture (l'`Id` d'un `users`, d'une `classe`…). Un `foreign_key` du contrat
  d'entité est traité comme un entier quelconque.

- **Impact** : impossible de produire des données **reliées** (élève → compte,
  inscription → élève + classe, progression → élève + affectation…). C'est le
  blocage principal pour tout scénario cohérent.

- **Correctif proposé** : un mécanisme de **références nommées** entre fixtures. Par
  exemple, une factory déclare des lignes avec un alias, et une autre le référence :
  ```python
  # users_factory : nomme les lignes
  self.row(alias="user_eleve", email="eleve@…", password_hash=…)
  # eleve_factory : résout l'Id de l'alias
  {"user_id": self.ref("user_eleve")}
  ```
  À la génération, `ref(...)` résout vers l'`Id` réel (ou un placeholder
  `LAST_INSERT_ID`/sous-requête `SELECT Id FROM users WHERE email=…`). Alternative :
  reconnaître les champs `foreign_key` du contrat et proposer un provider
  « référence » plutôt que `random_int`.

### F44 — `fixtures:load` **n'ordonne pas** par dépendances FK

- **Symptôme** : `fixtures:load` charge les `mvc/fixtures/*.sql` sans ordre déclaré
  ni tri par dépendances. Or les FK imposent un ordre (`users` avant `eleve`,
  `classe` avant `inscription_eleve`, `annee_scolaire` avant `classe`…). Un chargement
  en ordre alphabétique de fichiers échoue sur les contraintes.

- **Correctif proposé** : ordonner le chargement selon le **graphe de dépendances**
  des entités (déduit de `relations.json` / des FK), ou permettre de **déclarer** un
  ordre (préfixe numérique, ou clé `depends_on` dans la factory). À défaut, offrir un
  drapeau documenté pour désactiver les FK le temps du chargement (`SET
  FOREIGN_KEY_CHECKS=0`), comme le fait un reset de seed.

### F45 — SQL généré en **noms de champs** (snake_case), pas en **colonnes** d'entité

- **Symptôme** : le SQL cible `INSERT INTO eleve (nom, prenom, identifiant,
  date_naissance, user_id)`, alors que les **colonnes** générées par le moteur
  d'entités sont en **PascalCase** (`Nom`, `Prenom`, `Identifiant`, `DateNaissance`,
  `UserId`). MariaDB **tolère** (noms de colonnes insensibles à la casse), mais c'est
  **fragile** : sur PostgreSQL (sensible à la casse) l'`INSERT` échouerait.

- **Correctif proposé** : générer le SQL avec les **colonnes réelles** de
  `mvc/entities/<e>/<e>.sql` (mapping champ → colonne), pas les noms de champs du
  contrat. Cohérent avec « le SQL généré doit tourner sur le backend installé »
  (ADR-075).

## Ce qui reste **hors périmètre** fixtures (légitimement)

Deux parties du seed relèvent de la **logique métier**, pas des fixtures SQL :

- **Import du référentiel** depuis le **JSON canonique** (`import_referentiel`) — la
  source est un canonique, pas un dump SQL (cadre projet : « JSON canonique = source
  de construction »).
- **Bilan élève** — valeur **calculée** par agrégation des évaluations
  (`creer_bilan`), pas des données saisies.

**Piste (facultative) pour couvrir 100 %** : permettre des **fixtures « callable »**
(un hook Python exécuté par `fixtures:load`, pas seulement des `.sql`), pour brancher
un post-traitement métier (import canonique, agrégations). Sinon, ces deux étapes
restent dans un petit script applicatif appelé après `fixtures:load`.

## Synthèse

Avec **F43** (références) + **F44** (ordre) — et accessoirement **F45** (colonnes) —
`forge-mvc-fixtures` pourrait exprimer **tout le socle + parcours + comptes +
évaluations** de `seed_demo.py` en fixtures natives cohérentes. Resteraient hors
fixtures l'import du référentiel et le calcul du bilan (post-hook applicatif, ou
fixtures « callable » si la piste ci-dessus est retenue). En attendant, le projet
conserve `tools/seed_demo.py`.

## Suivi (2026-07-12, sha `b2463149`)

**F43, F44 et F45 sont résolus** côté Forge, vérifiés end-to-end :

- **F43** : `Factory.reference(table, key_column, value)` (ADR-077) rend la FK en
  **sous-requête** — ex. `classe.annee_scolaire_id = (SELECT Id FROM annee_scolaire
  WHERE Libelle = '2025-2026' LIMIT 1)`. Intégrité garantie, résolution à la charge.
- **F44** : `fixtures:load` fait le **tri topologique** des dépendances FK
  (`_fk_dependencies` + `_topological_order` depuis `relations.json`) — l'ordre
  observé est `annee_scolaire → niveau_classe → classe`.
- **F45** : le SQL généré utilise les **colonnes d'entité** (`Nom`, `UserId`,
  `CreatedAt`…), plus les noms de champs snake_case.

### F46 — `fixtures:generate` n'inclut pas les colonnes **timestamps** (NOT NULL)

- **Symptôme** : pour une entité `options.timestamps: true`, le `.sql` d'entité
  déclare `CreatedAt DATETIME NOT NULL` et `UpdatedAt DATETIME NOT NULL` **sans
  DEFAULT** (les timestamps sont posés par la couche applicative, ex. `NOW()` dans le
  CRUD généré / `referentiel_importer`). Or `fixtures:generate` **n'émet pas** ces
  colonnes : l'`INSERT` produit viole `NOT NULL` → `fixtures:load` échoue
  (`Field 'CreatedAt' doesn't have a default value`).

- **Contournement (projet)** : ajouter `CreatedAt`/`UpdatedAt` (valeur fixe) à la
  main dans **chaque** factory — lourd et facile à oublier sur ~20 entités.

- **Correctif proposé** : quand le contrat a `options.timestamps: true`, que
  `fixtures:generate` **ajoute automatiquement** `CreatedAt`/`UpdatedAt` (horodatage
  courant, ou une constante déterministe pour la reproductibilité, cf. `--seed`).
  Alternative : le moteur d'entités pose `DEFAULT CURRENT_TIMESTAMP` sur ces colonnes
  — mais ça change le schéma de toutes les entités, moins ciblé.

- **RÉSOLU (2026-07-12, sha `514896b6`)** : `fixtures:generate` ajoute désormais
  `CreatedAt`/`UpdatedAt` (valeur déterministe, ex. `2024-01-01 00:00:00`) pour les
  entités `timestamps: true`, sans que la factory ait à les fournir.

### Vérifié — tables **sans contrat** d'entité (socle auth)

`fixtures:generate users` fonctionne bien qu'`users` **n'ait pas** de contrat
`mvc/entities/` : une factory avec `rows()` explicite génère l'INSERT depuis les clés
du dict. Les comptes (`users`, `roles`, `user_roles`) sont donc **exprimables** en
fixtures (avec `hash_password` appelé dans la factory). Pas un manque.

### F48 — Pas de fixtures « callable » : la logique métier reste hors du pipeline

- **Contexte** : pour que le seed passe **entièrement** par les fixtures (objectif
  projet : `forge-mvc-fixtures` autosuffisant, plus de script de seed maison), il faut
  couvrir deux étapes qui ne sont **pas** des données statiques :
  - **import d'un référentiel** depuis son **JSON canonique** (`import_referentiel`) —
    le figer en `.sql` dupliquerait 81 objets et perdrait la source canonique (cadre
    projet : « JSON canonique = source de construction ») ;
  - **bilan élève** — valeur **calculée** par agrégation (`creer_bilan`).

- **Symptôme** : `fixtures:load` ne charge que des `mvc/fixtures/*.sql` ; l'opt-in
  n'expose que `Factory` / `FixtureReference`. Aucun moyen d'exécuter du **code Python**
  dans le pipeline de chargement.

- **Correctif proposé** : supporter des **fixtures « callable »** — p. ex.
  `mvc/fixtures/*.py` exposant une fonction `load()` (ou une classe), exécutée par
  `fixtures:load` **dans l'ordre des dépendances** (avec les `.sql`), pour brancher la
  logique métier (import canonique, agrégations). C'est le motif « seeder » classique
  (Laravel/Django). Ainsi un seed complet = fixtures `.sql` (comptes, socle, bloc B) +
  fixtures callable (référentiel, bilan), sans script externe.

- **RÉSOLU (2026-07-12, sha `5c7d30c3`)** : classe `Fixture` (ADR-078) — `tables`,
  `depends_on`, `load()` écrivant via `core.database.db`. `fixtures:load` découvre les
  `mvc/fixtures/*.py`, les ordonne avec les `.sql`, affiche leur source, exécute
  `load()` sur `--run`. Deux frottements apparaissent à l'usage (F49, F50).

### F49 — Une fixture callable ne peut pas importer le code applicatif (`mvc.*`)

- **Symptôme** : une fixture `mvc/fixtures/referentiel.py` qui fait
  `from mvc.services.referentiel_importer import import_referentiel` échoue au
  chargement : `fixtures:load` → **`No module named 'mvc'`**.

- **Cause** : `fixtures:load` importe le fichier sans placer la **racine du projet**
  dans `sys.path`. Or l'intérêt d'une fixture callable est justement d'appeler le code
  applicatif (`mvc.services.*`) — comme le fait `import config` pour les autres
  commandes.

- **Contournement (projet)** : `sys.path.insert(0, parents[2])` en tête de chaque
  fixture — répétitif et fragile.

- **Correctif proposé** : que `fixtures:load` insère la racine du projet dans
  `sys.path` (ou charge `config`) avant d'importer les `mvc/fixtures/*.py`, pour que
  `import mvc.…` fonctionne comme partout ailleurs dans le projet.

### F50 — L'ordre topologique ne relie pas une table **fournie par un callable** à un `.sql` dépendant

- **Symptôme** : avec `referentiel.py` (callable, `tables=(…, "niveau_classe", …)`) et
  `classe.sql` (factory, FK `niveau_classe_id` en sous-requête), `fixtures:load`
  ordonne `annee.sql → classe.sql → referentiel.py → …` : la **classe** est chargée
  **avant** le référentiel qui crée `niveau_classe`. La sous-requête
  `(SELECT Id FROM niveau_classe …)` renvoie alors `NULL` → FK violée.

- **Cause** : le tri semble traiter les `.sql` et les `.py` en deux blocs, ou ne
  **satisfait pas** la dépendance FK d'un `.sql` (`Classe → NiveauClasse`, via
  `relations.json`) par la table déclarée dans `Fixture.tables` d'un callable. La
  table `niveau_classe` fournie par `referentiel.py` devrait précéder `classe.sql`.

- **Correctif proposé** : un **graphe d'ordonnancement unifié** où chaque unité
  (`.sql` ou `.py`) **fournit** des tables (`table` de la factory / `tables` du
  callable) et **dépend** de tables (FK de `relations.json` + `depends_on`). Une unité
  qui dépend de `niveau_classe` doit être ordonnée après **toute** unité qui la
  fournit, `.sql` comme `.py`.

- **RÉSOLU (2026-07-12, sha `3ab0699d`)** : F49 (racine dans `sys.path` avant import
  des callable) et F50 (graphe unifié `.sql`/callable) corrigés. Un seed mixte
  (référentiel callable + socle `.sql`) charge dans le bon ordre. Reste F51.

### F51 — Une `reference()` vers une table **hors `relations.json`** n'ordonne pas

- **Symptôme** : `eleve.sql`/`professeur.sql` (factories) contiennent
  `UserId = (SELECT Id FROM users WHERE email = … LIMIT 1)` (via `reference("users",
  "email", …)`). Ils sont ordonnés **avant** `comptes.py` (callable, `tables=("users",
  …)`) → la sous-requête renvoie `NULL` : `Dupont.UserId = NULL`, `Bernard.UserId =
  NULL`. Les fiches ne sont **pas** reliées à leur compte (login sans données).

- **Cause** : l'ordre (F50) relie les dépendances issues de `relations.json` (FK entre
  **entités**), mais **pas** celles déclarées par `reference(table, …)` d'une factory
  quand `table` n'est **pas** une entité `mvc/entities/` (ex. `users`, socle auth). La
  dépendance `eleve → users` est donc invisible au tri.

- **Correctif proposé** : traiter chaque `reference(table, …)` d'une factory comme une
  **dépendance** vers `table` dans le graphe d'ordonnancement (au même titre qu'une FK
  `relations.json` ou un `depends_on`). Ainsi une factory qui référence `users` passe
  après l'unité (`.sql` ou callable) qui **fournit** `users`. C'est le complément
  naturel de F50, étendu aux tables hors contrat.

- **RÉSOLU (2026-07-12, sha `df822976`)** : une `reference(table, …)` est désormais une
  dépendance d'ordre. `fixtures:load --run` sur base propre relie correctement
  `eleve.UserId`/`professeur.UserId` à leur compte. Le seed complet
  (comptes + référentiel + socle + bloc B + bilan) charge de façon cohérente ; l'app
  a été vérifiée par rôle (prof voit sa classe et le bilan, élève son parcours, admin
  le socle).

### F52 — `fixtures:purge` ne supprime pas dans l'ordre **inverse** des dépendances

- **Symptôme** : `fixtures:purge --run` puis `fixtures:load --run` échoue :
  `Duplicate entry '2025-2026' for key 'uk_annee_scolaire_libelle'`. La purge émet
  `DELETE FROM classe; DELETE FROM annee_scolaire; DELETE FROM
  affectation_professeur_classe; …` : `annee_scolaire` (parent) est supprimée **avant**
  `affectation_professeur_classe` (enfant qui la référence) → le `DELETE` de
  `annee_scolaire` est bloqué par la FK, la ligne reste, et le `load` suivant tombe sur
  un doublon. Le cycle « rejouable » (`purge` + `load`) est donc cassé.

- **Cause** : `fixtures:purge` n'ordonne pas les `DELETE` en **inverse** du graphe de
  chargement (enfants avant parents), et n'encadre pas la purge par
  `SET FOREIGN_KEY_CHECKS=0/1`.

- **Correctif proposé** : purger dans l'ordre **inverse** de `fixtures:load` (le même
  graphe topologique, renversé), ou encadrer la purge par
  `SET FOREIGN_KEY_CHECKS=0` … `=1`. Objectif : `fixtures:purge --run &&
  fixtures:load --run` reconstruit un état propre de façon **idempotente** (données de
  démo rejouables, cf. `fixtures:load --help`).

- **Partiellement résolu (2026-07-12, sha `d3bedd72`)** : la purge se fait maintenant
  dans l'**ordre inverse du chargement** *entre* fixtures. **Mais** le démontage d'une
  fixture **callable multi-tables** échoue sur ses FK **internes** : `referentiel.py`
  déclare `tables=(…, "referentiel_niveau_classe", "niveau_classe", "competence", …)` ;
  au purge, `niveau_classe` est supprimée avant `referentiel_niveau_classe` qui la
  référence → `Cannot delete or update a parent row`. Les tables d'un même callable ne
  sont pas ordonnées entre elles.

- **Correctif restant proposé** : encadrer **toute** la purge par
  `SET FOREIGN_KEY_CHECKS = 0` … `= 1` (simple, robuste, indépendant de l'ordre
  interne), ou ordonner aussi les tables **au sein** d'un callable par le graphe FK
  avant suppression. Objectif inchangé : `fixtures:purge --run && fixtures:load --run`
  **idempotent**, y compris avec des callable peuplant plusieurs tables liées.

### F52-bis — `FOREIGN_KEY_CHECKS=0/1` émis sur le **pool** est sans effet (cause du non-correctif `1373b228`)

- **Symptôme** : après `1373b228` (encadrement de la purge par
  `foreign_key_checks_ddl`), `fixtures:purge --run` échoue **à l'identique** :
  `Cannot delete or update a parent row … referentiel_niveau_classe → niveau_classe`.
  Le cycle laisse la base à mi-chemin (purge partielle → `load` suivant bloqué sur
  `bloc_b : dépendance introuvable`).

- **Cause (révélée)** : `SET FOREIGN_KEY_CHECKS` est une variable de **session**
  (par connexion). Or `db.execute()` **sans `tx`** emprunte une connexion du **pool**
  (`get_connection()`), `commit()`, puis la **restitue** (`close_connection`). Le
  `db.execute("SET FOREIGN_KEY_CHECKS=0")` du CLI ne désactive donc les FK que sur la
  connexion empruntée pour *ce seul* statement, aussitôt rendue au pool ; chaque
  `DELETE` suivant repioche une connexion (pool_size=5) où les FK sont **toujours
  actives**. Pire : `Fixture.purge()` par défaut (`factory.py`, `db.execute(f"DELETE
  FROM {table}")` **sans `tx`**) tourne lui aussi hors de toute session FK-off — c'est
  exactement le callable `referentiel.py` qui casse.

- **Correctif proposé** : dérouler **tout** le démontage dans **une seule connexion**,
  via `with transaction() as tx:` (`core.database.transaction`), et passer **`tx=tx`**
  à *tous* les `db.execute` — le `SET … = 0`, les `DELETE`, le `SET … = 1`. Il faut donc
  aussi que **`Fixture.purge()` accepte et propage un `tx`** (ex. `purge(self, *, tx=None)`
  passé par le CLI), sinon le démontage des callables retombe sur le pool et le
  `FOREIGN_KEY_CHECKS=0` ne « voit » jamais leurs `DELETE`. Alternative sans FK-off :
  ordonner topologiquement **toutes** les tables (inter- **et** intra-callable) via
  `relations.json` et supprimer en une passe transactionnelle unique.

- **Critère d'acceptation** : `fixtures:purge --run && fixtures:load --run` **idempotent**
  (≥ 2 cycles sans erreur FK ni doublon), callable multi-tables (`referentiel.py`,
  15 tables liées) inclus, sur backend MariaDB **avec pool** (`DB_POOL_SIZE` ≥ 2).

- **Résolu (2026-07-12, sha `38501db6`)** : le démontage se déroule désormais dans une
  **connexion unique** (transaction partagée), `FOREIGN_KEY_CHECKS=0/1` et les `DELETE`
  — callables inclus — sur la **même** session. Vérifié banc d'essai : `fixtures:purge
  --run && fixtures:load --run` rejoué **2 cycles** (`rc=0`, aucune erreur FK ni doublon),
  état final cohérent (`referentiel.py` 15 tables, `bloc_b`, `bilan`). **F52 clos.** La
  bascule est actée : `tools/seed_demo.py` supprimé, `mvc/fixtures/` fait foi.

## Référence

`forge_mvc_fixtures/factory.py` (`Factory.reference/definition/rows/build`),
`forge_mvc_fixtures/cli/{generate,load}.py` (`_topological_order`, `reference` →
sous-requête). Preuve F46 : `fixtures:generate annee_scolaire` (INSERT sans
`CreatedAt`/`UpdatedAt`).
