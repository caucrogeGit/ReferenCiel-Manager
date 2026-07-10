# Retour terrain 016 — `forge-mvc-sessions-db` : hors catalogue, table non provisionnée, read-modify-write non transactionnel

**Destinataire :** équipe Forge (dépôt `caucrogeGit/Forge`).
**Émetteur :** projet RéférenCiel Manager (banc d'essai, ADR-005).
**Statut :** **résolu** côté Forge (6/6) ; upgrade projet appliqué (opt-in + cœur sur `5dbb382`).

> ## ✅ Résolu — Forge `5dbb382` (2026-07-10)
>
> **Les 6 constats corrigés** côté framework et **vérifiés sur le banc d'essai**
> (upgrade opt-in + cœur, `make check` vert, test fonctionnel du store, drive
> HTTP authentifié) :
>
> | Constat | Correctif (Forge) | Vérif |
> |---|---|---|
> | **F33** | `sessions-db` inscrit au **catalogue** `forge opt-in:list` (`cli/optins/catalog.py`) — livré dans le **cœur/CLI**, visible après upgrade de `forge-mvc` | ✅ |
> | **F34** | Migration livrée (`forge_mvc_sessions_db/migrations/20260710130000`) + commande `forge sessions:init` (ADR-071) | ✅ |
> | **F35** | Commande `forge sessions:gc` (purge sans dépendre de `jobs`) | ✅ |
> | **F36** | Store durci : concurrence optimiste (colonne `version` + garde `WHERE version = ?` + retry), flash lu une seule fois | ✅ |
> | **F37** | Horodatages en **UTC** (`timezone.utc`), Python seule autorité (plus de `DEFAULT`/`ON UPDATE` SGBD) | ✅ |
> | **F38** | Warning squelette pointe l'opt-in `sessions-db` au lieu de l'ADR-002 fantôme (`517956f`) | ✅ |
>
> **Bonus Forge** : **ADR-071** — convention unique de provisioning des opt-ins
> adossés à la base (migration versionnée + `migration:apply`) ; le cœur retire
> son `MariaDbSessionStore` intégré au profit de l'opt-in `DbSessionStore`.
>
> **Upgrade projet appliqué** : opt-in `sessions-db` **et** cœur `forge-mvc`
> (+ CLI + `entities`) reinstallés sur `5dbb382` ; migration de réconciliation
> `20260710195527_align_forge_sessions_v2` (ajout `version`, retrait des defauts
> SGBD des horodatages) ; warning `app.py` aligné sur le squelette corrigé.
>
> **Suite optionnelle** : F33 étant levé, l'inscription manuelle de `sessions-db`
> dans `optins/registry.py` (hors bloc géré) pourrait être remplacée par
> `forge opt-in:enable sessions-db` — reconciliation non bloquante, non encore faite.

## Environnement

- `forge-mvc` **1.0.0rc2**, backend `forge-mvc-mariadb` **1.0.0rc2**,
  nouvel opt-in **`forge-mvc-sessions-db` 1.0.0rc2**, Python 3.12.
- Installé par pip depuis le monorepo Forge :
  `pip install "git+https://github.com/caucrogeGit/Forge.git@main#subdirectory=packages/forge-mvc-sessions-db"`.
- Contexte : remplacer le `MemorySessionStore` par défaut (mono-processus, perdu
  au redémarrage) par un store persistant partagé, en prévision du multi-worker.
- Intégration réalisée : migration projet `create_forge_sessions`, activation via
  `forge.configure(session_store=DbSessionStore(ttl=SESSION_TTL))`, purge à câbler.

## Ce qui fonctionne bien (à conserver)

- Contrat d'activation propre : un seul `forge.configure(session_store=…)`, sans
  magie ni monkeypatch ; le warning `emit_memory_store_warning_if_needed` s'éteint
  de lui-même une fois le store non-mémoire posé.
- Import paresseux de la base (`_default_fetch_one`/`_execute` importent
  `core.database.db` à l'appel) : l'app démarre sans connexion à l'import.
- Accesseurs `fetch_one`/`execute` **injectables** → store testable sans base.
- Contrat `SessionStore` complet et dépendance opt-in → cœur (principe 8) respectée.

Les constats ci-dessous portent sur le **packaging**, le **provisioning** et la
**concurrence**, pas sur le contrat fonctionnel.

## Constats

### F33 — L'opt-in est absent du catalogue `forge opt-in:list` et non géré par la CLI

- **Symptôme** :

  ```console
  $ forge opt-in:list | grep -i session      # → rien
  $ forge opt-in:enable sessions-db
  [ERREUR] opt-in inconnu : sessions-db
  Opt-ins officiels : admin, audio, audit, deploy, files, i18n, images,
  import-export, iot, jobs, mail, mfa, notifications, qrcode, rbac, settings,
  stats, video, workflow
  Pour un module local que vous écrivez vous-même, voir : forge module:install
  ```

- **Cause** — `forge-mvc-sessions-db` est pourtant un paquet **du monorepo Forge**
  (`packages/forge-mvc-sessions-db`), au même titre que `files`, `rbac`, `admin`,
  mais il ne figure pas dans le catalogue des opt-ins officiels. La seule voie
  d'installation est `pip … #subdirectory=…` ; aucune commande `forge` ne le
  connaît, donc `optins/registry.py` (ADR-061) doit être **édité à la main**,
  hors des marqueurs gérés par `forge opt-in:enable`.

- **Conséquence** : incohérence de traitement entre opt-ins du même dépôt. Un
  opt-in officiel invisible du catalogue est indécouvrable ; le registre du projet
  perd sa complétude si l'ajout manuel est oublié.

- **Suggestion** : soit **inscrire `sessions-db` au catalogue** `forge opt-in:list`
  (c'est un paquet Forge, pas un module tiers), soit, s'il reste hors catalogue à
  dessein, **documenter le chemin `forge module:install`** dans la notice de
  l'opt-in plutôt que de laisser le porteur éditer le registre à la main.

### F34 — Aucune table livrée : ni `.sql`, ni migration, ni commande de provisioning (et DDL mono-backend)

- **Symptôme** : le store suppose la table `forge_sessions` mais le paquet ne
  contient **aucun fichier `.sql`** — uniquement `__init__.py`, `store.py`,
  `py.typed`. Le DDL doit être recopié **à la main** depuis la notice dans une
  migration projet.

- **Aggravant 1 — docstring trompeur** : `store.py` annonce

  ```python
  # store.py, en-tête de module
  Table requise : voir `mvc/models/sql/forge_sessions.sql`.
  ```

  Ce fichier **n'existe pas** (ni dans le paquet, ni généré dans le projet). La
  référence pointe vers un chemin fantôme.

- **Aggravant 2 — portabilité à moitié tenue** : le module se présente comme
  « agnostique du SGBD… portable » (et l'est côté SQL : horodatages paramétrés,
  pas de `NOW()`/`GETDATE()`/`datetime('now')`). Mais la **notice ne fournit que
  le DDL MariaDB**. Le store est portable, **son provisioning ne l'est pas** : à
  chaque projet de réécrire la table pour SQLite/Postgres/MSSQL.

- **Conséquence** : récurrence du même manque déjà signalé en **retour-006** et
  **retour-015** — les opt-ins adossés à la base ne livrent pas leur schéma. Le
  porteur provisionne à la main, sans garde-fou de cohérence type/colonnes.

- **Suggestion** : livrer le DDL **par backend** (dossier `sql/` de l'opt-in ou
  migration fournie) **et** une commande de provisioning (`sessions:init`), sur le
  modèle de ce qui manquait déjà au socle auth/RBAC. À défaut, corriger la
  référence de chemin du docstring et fournir les DDL des 4 backends dans la notice.

### F35 — `cleanup_expired()` sans planificateur dans l'écosystème ; `jobs` ne répond pas au besoin

- **Symptôme** : `cleanup_expired()` est documenté « à câbler sur une tâche
  planifiée », mais Forge n'offre **aucun planificateur**. L'opt-in le plus
  proche, `forge-mvc-jobs`, est une **file de tâches** (`enqueue`, `drain`,
  `run_worker` — boucle de polling), **pas un cron** : il faut quand même un
  déclencheur temporel externe pour enfiler la purge. Installer `jobs` déplace le
  problème sans le résoudre (dépendance + table de file en plus).

- **Conséquence** : chaque projet réimplémente le même script + cron/systemd timer
  pour une purge pourtant standard, offerte par le contrat du store.

- **Suggestion** : exposer une **commande CLI** (p. ex. `sessions:gc`) que le
  projet branche sur cron/systemd, ou fournir une brique de tâche périodique
  distincte de la file `jobs`. Idéalement, documenter le pattern recommandé dans
  la notice de l'opt-in.

### F36 — Read-modify-write **non transactionnel** : les garanties d'atomicité ne sont pas tenues (défaut le plus important)

- **Symptôme** : `set`, `replace`, `touch_expiry`, `authenticate` et `get_flash`
  procèdent en deux temps — un `fetch_one` (lecture) **puis** un `execute`
  (écriture) — sans transaction englobante :

  ```python
  # get_flash — docstring : « Lit et supprime atomiquement le message flash »
  data = self._load(session_id)          # SELECT  → connexion A, COMMIT
  flash = data.pop("flash", None)
  if flash is not None:
      self._execute(_SQL_UPDATE, …)      # UPDATE  → connexion B, COMMIT
  ```

- **Cause** — via `core.database.db`, **chaque** appel emprunte une connexion du
  pool, exécute **une** instruction et **committe**, y compris après un SELECT :

  ```python
  # core/database/db.py::_run_query
  if owns_connection:
      connection.commit()   # commit même après SELECT (sinon snapshot figé au retour au pool)
  ```

  Le `SELECT` et l'`UPDATE`/`DELETE` s'exécutent donc sur **deux connexions
  distinctes, en deux transactions committées séparément, sans verrou**. Le store
  n'expose aucun moyen d'englober les deux (`_default_fetch_one`/`_execute` ne
  passent pas de paramètre `tx`, alors que `core.database.transaction` existe).

- **Conséquence** — la course n'est **pas** cantonnée au multi-worker : le serveur
  applicatif est `ThreadingHTTPServer` (mono-worker **multi-thread**), donc deux
  requêtes concurrentes sur le **même** `session_id` se marchent dessus **dès le
  mode dev**, a fortiori en multi-worker — le cas d'usage même de l'opt-in :
  - `get_flash` : deux requêtes lisent le même flash avant que l'une le supprime
    → **flash affiché deux fois** ; l'atomicité annoncée n'est pas tenue.
  - `set`/`touch_expiry`/`authenticate` : **lost update** — le dernier writer
    écrase les modifications concurrentes de `data` ; « Rotation atomique » (docstring
    de `authenticate`) n'est pas garantie.

- **Suggestion** : envelopper chaque read-modify-write dans **une seule**
  transaction (`core.database.transaction`) avec `SELECT … FOR UPDATE`, ou
  remplacer par des écritures **conditionnelles atomiques** (un seul `UPDATE …
  WHERE session_id = ?` côté serveur ; pour le flash, `DELETE … RETURNING` ou un
  `UPDATE … SET flash = NULL WHERE … AND flash IS NOT NULL` dont le `rowcount`
  décide qui « gagne »). À défaut de correction, **retirer le mot « atomique »**
  des docstrings pour ne pas promettre une garantie absente.

### F37 — Horodatages en heure locale naïve + double horloge SGBD/Python (à vérifier)

- **Symptôme** : `_dt`/`_now_str` s'appuient sur `datetime.fromtimestamp()` et
  `datetime.now()`, donc sur l'heure **locale naïve** du process.

- **Analyse** : la logique d'expiration reste **auto-cohérente** (valeurs posées et
  comparées côté Python). Deux réserves subsistent :
  1. **Fuseau/DST** : si le serveur change de fuseau ou traverse une bascule DST,
     les chaînes `YYYY-MM-DD HH:MM:SS` deviennent ambiguës (heure locale répétée).
  2. **Double horloge** : le DDL recommandé déclare `created_at DEFAULT
     CURRENT_TIMESTAMP` et `updated_at … ON UPDATE CURRENT_TIMESTAMP` (**horloge
     SGBD**), alors que le store écrit **aussi** ces colonnes en heure locale
     Python → deux autorités pour les mêmes colonnes, potentiellement désaccordées.

- **Suggestion** : horodater en **UTC** (`datetime.now(timezone.utc)`) et confier
  `created_at`/`updated_at` à **une seule** autorité (le SGBD via DEFAULT/ON UPDATE,
  *ou* Python — pas les deux).

- **Note mineure connexe** : le TTL par défaut du store persistant est importé de
  `core.sessions.memory_store.SESSION_TTL` — un store persistant qui tire son
  défaut du module *mémoire* est un couplage surprenant ; une constante neutre
  (contrat/config de session) serait plus lisible.

### F38 — Le warning multi-worker du squelette pointe vers un ADR de session inexistant (connexe, côté squelette)

- **Symptôme** : le squelette `app.py` avertit, en multi-worker :

  ```python
  logger.warning(
      "AVERTISSEMENT — Forge utilise des sessions mémoire … "
      "Voir ADR-002 : docs/adr/002-session-strategy.md"
  )
  ```

  Or `docs/adr/002-session-strategy.md` **n'existe pas** dans un projet Forge, et
  le numéro **entre en collision** avec la numérotation ADR du projet (ici
  ADR-002 = « JSON canonique et persistance applicative »). Le porteur qui suit le
  lien tombe à côté.

- **Suggestion** : faire pointer le warning vers la **notice de l'opt-in
  `sessions-db`** (ou une page Forge stable), pas vers un numéro d'ADR **projet**
  présumé — la numérotation ADR appartient au projet, pas au squelette.

## Contournement retenu côté projet

- Migration projet `create_forge_sessions` (DDL MariaDB de la notice), `db:apply`
  appliqué → table en place (esquive F34 côté projet).
- `SESSION_TTL` ajouté à `config.py` (env `SESSION_TTL`, défaut 3600) et passé au
  store ; activation dans `app.py`.
- Inscription **manuelle** de `sessions-db` dans `optins/registry.py`, **hors** du
  bloc géré par `forge opt-in:enable`, avec commentaire (contourne F33).
- Purge des sessions expirées : à câbler via une commande projet + cron/systemd
  (F35) — non encore réalisée.
- F36/F37 : **non contournables côté projet** (défauts internes au store) ;
  remontés tels quels.
