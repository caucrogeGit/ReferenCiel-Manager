# ADR-005 : Backend de base de données : MariaDB

## Statut

Accepté (2026-07-05).

> Décision du porteur du projet : le backend BDD est **MariaDB**.
> L'installation de l'opt-in `forge-mvc-mariadb` et la mise en place du serveur sont **à la charge du porteur**, le moment venu (prérequis du ticket 07).
> L'agent n'installe pas le backend.

## Date

2026-07-05

## Contexte

Le cœur de Forge est **agnostique BDD** : il découvre le backend installé par entry point (`forge_mvc.db_backend`), chaque SGBD étant un **opt-in exclusif** : **un seul backend par projet** (Forge ADR-054).
Le squelette est **livré sans backend** et sans configuration BDD ; installer un backend est une étape explicite, et la config BDD appartient au backend installé (Forge ADR-060).
Tant qu'aucun backend n'est présent, `forge doctor` le signale et tout `db:*` échoue.

Quatre backends sont publiés (Forge ADR-054) : `forge-mvc-mariadb` et `forge-mvc-sqlite` (complets, bout en bout), `forge-mvc-postgres` et `forge-mvc-mssql` (Alpha).
Le SQL reste **visible et natif** au SGBD choisi (pas d'ORM) : **changer de backend = réécrire le SQL**, le choix engage.

RéférenCiel Manager est une **application métier pédagogique persistée**.
Le porteur souhaite un backend **serveur**, proche des conditions réelles, à la fois pour lui-même et comme support d'apprentissage pour les élèves (infrastructure réelle).

## Décision

Le projet adopte **`forge-mvc-mariadb`** comme backend de base de données.

1. **Installation à la charge du porteur.**
   Le moment venu (avant le ticket 07, première tranche persistée), le porteur installe l'opt-in et met en place le serveur :

   ```bash
   pip install forge-mvc-mariadb   # + serveur MariaDB et comptes (voir doc du backend)
   ```

   L'agent **ne l'installe pas** et ne configure pas le serveur.

2. **Un seul backend par projet** : aucun autre backend n'est installé en parallèle.
   La configuration BDD (`DB_ADMIN_*` / `DB_APP_*`, hôte, port, `utf8mb4`, …) provient du backend (Forge ADR-060) et vit dans `env/` (hors dépôt).

3. **SQL natif MariaDB assumé** : le SQL généré/écrit cible MariaDB (`AUTO_INCREMENT`, `utf8mb4`, `INFORMATION_SCHEMA`, split admin/app).
   Cohérent avec le contrat d'entité Forge, dont le schéma décrit déjà des tables/index MariaDB.

4. **Validation** : après installation par le porteur, `forge doctor` doit passer avant tout `db:init`.

## Conséquences

- Une fois le backend installé par le porteur : `forge db:init`, `db:apply`, `migration:*`, `build:model` sont opérationnels ; la tranche verticale Bloc A (ticket 07) est débloquée.
- Environnement plus riche à mettre en place (serveur MariaDB + comptes), assumé par le porteur comme support d'apprentissage réel.
- Les tests marqués **`db`** exigent une **vraie MariaDB** : sautés en local sans base, requis en CI (modèle Forge : `FORGE_REQUIRE_DB=1`).
  Voir ADR-007.
- Le choix est durable : migrer vers un autre SGBD supposerait de réécrire le SQL natif et ferait l'objet d'un nouvel ADR.

## Alternatives écartées

- **`forge-mvc-sqlite`** : backend complet, sans serveur ni comptes (zéro friction), écarté sur **décision du porteur**, qui veut un backend serveur proche du réel pour l'expérience et l'apprentissage.
- **`forge-mvc-postgres` / `forge-mvc-mssql`** : statut **Alpha** → écartés pour une application qui doit être fiable.
- **Rester sans backend** : impossible, bloque tout `db:*` et donc la persistance, vérité applicative en fonctionnement (ADR-003).

## Suite

- Le porteur installe `forge-mvc-mariadb` + serveur, au plus tard avant le ticket 07.
- Le versionnement métier (`brouillon → publié → archive`) et les états de progression pourront s'appuyer sur l'opt-in `forge-mvc-workflow` (à évaluer).
