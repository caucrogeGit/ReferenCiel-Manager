# Retour terrain 023 : le pool MariaDB lève sans attente et s'épuise sous concurrence

**Destinataire :** équipe Forge (dépôt `caucrogeGit/Forge`).
**Émetteur :** projet RéférenCiel Manager (banc d'essai, ADR-006).
**Statut :** **Ouvert** (2026-07-19).

## Environnement

- `forge-mvc` (Core) **1.0.0rc2**, `forge-mvc-mariadb` **1.0.0rc2**,
  `forge-mvc-sessions-db` **1.0.0rc2**, Python 3.12, backend MariaDB.
- Contexte : crash tests de robustesse de l'application (entrées forgées, CSRF,
  RBAC, charge). Toutes les suites séquentielles passent (303 requêtes adverses,
  0 erreur serveur). Le constat ci-dessous n'apparaît que **sous concurrence**.

## Constat

### F59 : `backend.get_connection()` lève immédiatement quand le pool est vide (Défaut)

- **Symptôme** : sous une rafale de requêtes **simultanées** (30 threads, chemins
  mêlant login et pages authentifiées), une partie des réponses est **500**.
  En séquentiel, aucune. Reproduit avec le pool par défaut (`DB_POOL_SIZE`
  non défini → **5**) :

  ```
  Rafale 200 requêtes / 30 threads : {200: 103, 404: 49, 500: 48}
  ```

- **Cause** (trace serveur) : le pool `mariadb.ConnectionPool` est épuisé et
  `get_connection()` **ne patiente pas** — il lève `PoolError` aussitôt, qui
  remonte en 500 :

  ```
  mariadb.PoolError: No connection available
    → forge_mvc_sessions_db/store.py, create()        (session créée au login)
    → core/database/db.py, execute()
    → forge_mvc_mariadb/backend.py, get_connection()
    → mariadb/connectionpool.py, get_connection()
  ```

  Le backend attrape bien `PoolError`, le journalise (`logger.exception`) et le
  **ré-émet tel quel** : il n'y a ni file d'attente, ni délai d'attente, ni
  réessai. Toute requête qui touche la base au-delà de `pool_size` connexions
  actives échoue.

- **Impact — spécifique à ce type d'application** : le scénario d'usage central
  est *une classe entière (~30 élèves) qui se connecte quasi simultanément*
  quand le professeur lance la séance. Le login **crée une session en base**
  (`forge-mvc-sessions-db`), donc emprunte une connexion. Avec `pool_size=5`, la
  majorité des élèves reçoit un 500 au moment le plus visible du produit. Le pool
  **se rétablit** après le pic (connexions rendues), mais le mal est fait pendant
  la rafale.

- **Ce qui va bien** : la page 500 **n'expose aucune trace en production**
  (`core.errors.build_dev_error_context` renvoie `None` dès `APP_ENV != dev` —
  charte « sécurisé par défaut » respectée). La fuite de trace observée est
  **cantonnée au mode dev** (page de debug attendue).

- **Contournement appliqué (côté application)** : `DB_POOL_SIZE=32` posé dans
  `env/dev`, `env/prod` et `env/example`, dimensionné sur le pic « classe
  entière + marge ». C'est un **palliatif de capacité** : il déplace le seuil
  sans supprimer le mode d'échec — au-delà de `pool_size` requêtes DB
  simultanées, les 500 reviennent (et `ConnectionPool` plafonne à 64).

- **Attendu (côté Forge)** : que `backend.get_connection()` **attende** une
  connexion disponible pendant un délai borné avant d'abandonner, plutôt que de
  lever sur-le-champ. Pistes :
  - exposer et utiliser un `pool_timeout` (attente bornée sur l'emprunt), avec
    éventuellement un petit réessai ;
  - documenter `DB_POOL_SIZE` comme un dimensionnement de **concurrence** (pas
    seulement une valeur par défaut opaque), avec la borne haute (64) et le lien
    avec `forge-mvc-sessions-db` (le login consomme une connexion) ;
  - à défaut d'attente, renvoyer un **503 + Retry-After** plutôt qu'un 500, pour
    distinguer « surcharge temporaire » de « erreur applicative ».

## Synthèse

- **F59 (Défaut, robustesse)** : sous concurrence supérieure à `DB_POOL_SIZE`,
  `get_connection()` lève sans attendre → 500 au login pour une classe entière.
  Palliatif capacité posé côté app (`DB_POOL_SIZE=32`) ; correction durable
  attendue côté Forge (attente bornée / réessai, ou 503 explicite).

## Référence

- Config appliquée : `env/dev`, `env/prod`, `env/example` (clé `DB_POOL_SIZE`).
- Mode d'échec observé au niveau `forge_mvc_mariadb/backend.py`
  (`get_connection`) et `forge_mvc_sessions_db/store.py` (`create`).
