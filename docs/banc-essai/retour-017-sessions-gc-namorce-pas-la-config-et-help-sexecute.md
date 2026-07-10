# Retour terrain 017 — `forge sessions:gc` n'amorce pas la config projet ; `--help` s'exécute

**Destinataire :** équipe Forge (dépôt `caucrogeGit/Forge`).
**Émetteur :** projet RéférenCiel Manager (banc d'essai, ADR-005).
**Statut :** à remonter.

## Contexte

Suite du [retour-016](retour-016-sessions-db-hors-catalogue-schema-non-livre-et-read-modify-write-non-transactionnel.md)
(résolu 6/6). En branchant la purge des sessions (F35), on constate que la
commande livrée `forge sessions:gc` n'est **pas utilisable telle quelle**.

## Environnement

- `forge-mvc` **`5dbb382`**, `forge-mvc-mariadb` **`5dbb382`**,
  `forge-mvc-sessions-db` **`5dbb382`**, Python 3.12.
- Backend MariaDB, identifiants applicatifs chargés depuis `env/dev` (comme
  `app.py` / `forge run` / `forge migration:apply`).

## F39 — `forge sessions:gc` n'amorce pas la configuration du projet

- **Symptôme** :

  ```console
  $ forge sessions:gc
  ...
  mariadb.OperationalError: Access denied for user 'roger'@'localhost' (using password: NO)
  ```

  La commande tente `DbSessionStore().cleanup_expired()` sans identifiants : le
  pool MariaDB se rabat sur l'utilisateur système, **sans mot de passe**.

- **Cause** — le handler CLI de l'opt-in (`forge_mvc_sessions_db/cli/gc.py`)
  instancie le store et ouvre la connexion **sans avoir chargé la configuration
  du projet** (`env/dev`). Les commandes du cœur qui touchent la base
  (`forge run`, `forge migration:apply`) amorcent, elles, l'environnement. À noter
  que `config.py` charge l'env via `load_dotenv("env/example")` /
  `load_dotenv("env/dev")` en **chemins relatifs** : un contournement projet doit
  donc à la fois importer `config` **et** s'exécuter depuis la racine du projet
  (sinon `env/dev` n'est pas trouvé). La commande d'opt-in ne fait ni l'un ni l'autre.

- **Conséquence** — `sessions:gc` est **inutilisable en cron/systemd**, or c'est
  précisément l'usage prévu (purge périodique, réponse à F35). Le porteur doit
  réintroduire un script projet qui charge la config avant d'appeler le store.

- **Contournement projet** — `tools/sessions-gc.py` : se replace dans la racine
  projet (`os.chdir`), `import config` (charge `env/dev`), puis
  `DbSessionStore().cleanup_expired()`. Robuste au CWD → fonctionne en cron/systemd.

- **Suggestion** — faire amorcer la config du projet aux commandes CLI des opt-ins
  adossés à la base (comme `migration:apply`), afin qu'elles se connectent avec les
  mêmes identifiants applicatifs que le runtime.

## F40 — `--help` s'exécute au lieu d'afficher l'aide (commandes d'opt-in sessions-db)

- **Symptôme** : `forge sessions:gc --help` **lance la purge** (et ici plante,
  F39) au lieu d'afficher l'aide ; `forge sessions:init --help` **copie la
  migration** au lieu d'afficher l'aide.

- **Conséquence** — pas de découverte sûre de la commande : on ne peut pas lire
  son aide sans déclencher son effet. Écart de comportement avec les commandes du
  cœur, qui respectent `--help`.

- **Suggestion** — intercepter `-h/--help` dans le dispatch des commandes d'opt-in
  (ou dans chaque handler) avant d'exécuter l'effet.

## Portée

Constats **côté CLI d'opt-in**, sans rapport avec le contrat fonctionnel du store
(durci et validé en retour-016). Non bloquants pour le projet grâce au
contournement, mais ils annulent l'intérêt de commandes pourtant livrées.
