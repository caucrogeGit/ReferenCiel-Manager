# ADR-004 — Backend de base de données : SQLite

## Statut

Proposé.

> Décision structurante en attente de validation. Elle choisit le **backend BDD**
> du projet. Prérequis de toute opération `forge db:*` / migration, donc du ticket
> de tranche verticale Bloc A (ticket 07). Le ticket 02 (contrat JSON canonique)
> en est indépendant.

## Date

2026-07-05

## Contexte

Le cœur de Forge est **agnostique BDD** : il définit un contrat de backend et
découvre le backend installé par entry point (`forge_mvc.db_backend`), chaque SGBD
étant un **opt-in exclusif** — **un seul backend par projet** (Forge ADR-054). Le
squelette est **livré sans backend** et sans configuration BDD : installer un
backend est la première étape explicite après `forge new`, et la config BDD
appartient au backend installé (Forge ADR-060).

Conséquence directe et vérifiée sur ce dépôt : `forge doctor` signale
« aucun backend BDD installé », et **tout `db:init` / `db:apply` / migration échoue**
tant qu'aucun `forge-mvc-<backend>` n'est présent.

Quatre backends sont publiés (Forge ADR-054) :

- **`forge-mvc-sqlite`** — complet, bout en bout ;
- **`forge-mvc-mariadb`** — complet, bout en bout ;
- **`forge-mvc-postgres`** — **Alpha** (intégration réelle à valider) ;
- **`forge-mvc-mssql`** — **Alpha** (intégration réelle à valider).

Contraintes de charte : le SQL reste **visible et natif** au SGBD choisi (pas
d'ORM, pas de portabilité promise). **Changer de backend = réécrire le SQL** : le
choix engage.

RéférenCiel Manager est une **application métier pédagogique** : elle doit
s'installer et tourner **sans friction** pour un professeur et des élèves, sans
serveur ni comptes à administrer.

## Décision

Le projet adopte **`forge-mvc-sqlite`** comme backend de base de données.

1. Backend installé explicitement :

   ```bash
   pip install forge-mvc-sqlite
   ```

   et épinglé dans le `requirements.txt` du projet (au même titre que `forge-mvc`).

2. SQLite s'appuie sur le module `sqlite3` de la **bibliothèque standard** :
   **aucune dépendance externe, aucun serveur, aucun compte**. Base = un fichier.

3. **Un seul backend par projet** : on n'installe aucun autre backend
   (`forge-mvc-mariadb`, etc.) en parallèle. La config BDD provient du backend
   (Forge ADR-060).

4. Après installation, on valide avec `forge doctor` avant tout `db:init`.

## Conséquences

- `forge db:init`, `forge db:apply`, `forge migration:*`, `build:model`
  deviennent opérationnels ; la tranche verticale Bloc A (ticket 07) est débloquée.
- Zéro infrastructure : dépôt autoportant, démarrage immédiat, tests simples
  (compatibles `forge-mvc-testing`).
- Le SQL généré/écrit est du **SQLite natif assumé**. Une migration ultérieure
  vers MariaDB/PostgreSQL resterait possible (cœur agnostique) mais impliquerait de
  **réécrire le SQL** : ce n'est pas gratuit et se déciderait par un nouvel ADR.
- Si un besoin de déploiement multi-utilisateurs à forte concurrence apparaissait,
  on réévaluerait le backend (SQLite reste adapté à un usage classe/établissement,
  pas à une charge serveur intensive).

## Alternatives écartées

- **`forge-mvc-mariadb`** : backend complet, mais **serveur + comptes** à
  administrer → friction contraire à l'objectif pédagogique. Réservé à un
  éventuel déploiement ultérieur, par ADR.
- **`forge-mvc-postgres` / `forge-mvc-mssql`** : statut **Alpha** (intégration à
  valider) → écartés pour une application qui doit « juste marcher ».
- **Rester sans backend** : impossible — bloque tout `db:*` et donc toute
  persistance, qui est la vérité applicative en fonctionnement (ADR-002).

## Suite

- Faire valider cet ADR (**Proposé → Accepté**).
- Une fois accepté : `pip install forge-mvc-sqlite`, épingler dans
  `requirements.txt`, vérifier `forge doctor`. Prérequis du ticket 07.
- Le versionnement métier (`brouillon → publié → archive`) et les états de
  progression (Bloc B) pourront s'appuyer sur l'opt-in **`forge-mvc-workflow`**
  (statuts et transitions) — à évaluer le moment venu, pas requis maintenant.
