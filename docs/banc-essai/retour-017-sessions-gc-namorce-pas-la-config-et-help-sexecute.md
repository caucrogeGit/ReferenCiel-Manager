# Retour terrain 017 — `forge sessions:gc` n'amorce pas la config projet ; `--help` s'exécute

**Destinataire :** équipe Forge (dépôt `caucrogeGit/Forge`).
**Émetteur :** projet RéférenCiel Manager (banc d'essai, ADR-006).
**Statut :** **résolu** côté Forge (2/2) ; contournement projet retiré.

> ## ✅ Résolu — Forge `2f2386a` (ADR-072, 2026-07-10)
>
> `fix(cli): amorçage config projet et interception --help pour les commandes
> d'opt-in`. **Les 2 constats corrigés**, vérifiés sur le banc (upgrade sur
> `2f2386ab`) :
>
> | Constat | Correctif (Forge) | Vérif |
> |---|---|---|
> | **F39** | Drapeau déclaratif `config: True` dans la table `COMMANDS` de l'opt-in ; `dispatch_optin` amorce `load_project_config()` (`chdir` racine + `env/dev`) avant le handler. `sessions:gc` le pose. | ✅ `forge sessions:gc` purge sans `Access denied` |
> | **F40** | Filet **générique** dans `dispatch_optin` : `-h/--help` intercepté avant tout effet (aide riche si dispo, sinon ligne de repli) — couvre aussi les opt-ins tiers. | ✅ `sessions:gc --help` / `sessions:init --help` affichent l'aide, sans effet |
>
> **Conséquence projet** : le contournement `tools/sessions-gc.py` est **retiré** ;
> la purge (F35) se branche désormais sur la commande canonique
> `forge sessions:gc` (cron/systemd, depuis la racine du projet).

## Contexte

Suite du [retour-016](retour-016-sessions-db-hors-catalogue-schema-non-livre-et-read-modify-write-non-transactionnel.md)
(résolu 6/6). En branchant la purge des sessions (F35), on constate que la
commande livrée `forge sessions:gc` n'est **pas utilisable telle quelle**.

## Environnement

- `forge-mvc` **`5dbb382`**, `forge-mvc-mariadb` **`5dbb382`**,
  `forge-mvc-sessions-db` **`5dbb382`**, Python 3.12.
- Backend MariaDB, identifiants applicatifs chargés depuis `env/dev` (comme
  `app.py` / `forge run` / `forge migration:apply`).
- **Note** : le banc était sur `5dbb382`. Depuis, `main` est passé à `bded0bb`,
  qui **corrige déjà F40 pour les 3 commandes concernées** (voir F40 ci-dessous).
  F39 reste ouvert sur `bded0bb` (`cli/gc.py` inchangé).

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

## F40 — `--help` s'exécute au lieu d'afficher l'aide (corrigé ponctuellement ; garde générique manquant)

- **Symptôme observé (sur `5dbb382`)** : `forge sessions:gc --help` **lance la
  purge** (et plante, F39) ; `forge sessions:init --help` **copie la migration**.

- **Déjà corrigé pour ces commandes** — `bded0bb` (CLI-HELP-COVERAGE-OPTIN-INIT-001)
  a **enregistré** `sessions:gc`, `sessions:init` et `images:init` dans la
  couverture d'aide (`cli/_support/help_dispatch.py`). Le garde-fou central de
  `forge.py` (`wants_help(...)` → `format_command_help(command)` **avant**
  `dispatch_optin`) affiche alors l'aide et `return`. ✅ pour ces 3 commandes.

- **Résidu (le vrai fond)** — ce garde-fou est **basé sur un enregistrement
  manuel par commande** : `format_command_help()` renvoie `None` pour toute
  commande non listée, et le garde-fou ne fait alors rien. Or `dispatch_optin`
  (`cli/commands/optin_dispatch.py`) **n'intercepte pas `--help`** : **toute**
  commande d'opt-in non enregistrée (présente ou future, de n'importe quel opt-in)
  **s'exécute encore** sur `--help`. La couverture est un rattrapage au cas par
  cas, pas une garantie.

- **Suggestion** — ajouter un **filet générique dans `dispatch_optin`** :
  intercepter `-h/--help` avant d'invoquer le handler et afficher au minimum une
  aide de repli (docstring du handler / message neutre). Ainsi tout opt-in est
  couvert par défaut, sans dépendre d'un enregistrement manuel.

## Portée

Constats **côté CLI d'opt-in**, sans rapport avec le contrat fonctionnel du store
(durci et validé en retour-016). Non bloquants pour le projet grâce au
contournement, mais ils annulent l'intérêt de commandes pourtant livrées.
