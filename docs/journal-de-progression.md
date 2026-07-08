# Journal de progression — RéférenCiel Manager

> **Objet.** Ce document raconte, chapitre par chapitre, **ce qui a été fait**
> concrètement pour construire l'application : commandes lancées, entités créées,
> SQL généré, décisions prises (et pourquoi), blocages rencontrés. Il sert de
> **matière première** pour la future documentation du projet.
>
> **Comment le tenir.** À chaque nouvelle étape, on ajoute une sous-section datée
> avec : *contexte → commandes → résultat → décisions*. On relie aux ADR
> (`docs/adr/`) et aux retours banc d'essai (`docs/banc-essai/`) plutôt que de tout
> recopier.

---

## 1. Fondations documentaires

Avant tout code métier, le projet a posé sa **chaîne documentaire** :

- **Cadrage** : `docs/cadrage/instructions.md` (prioritaire), `cadre-projet-referenciel-manager.md`.
- **Décisions (ADR)** : `docs/adr/` — voir le [journal ADR](adr/index.md).
- **JSON canonique** : contrats + schémas + exemples (`docs/specs/json-canonique/`),
  pour deux types : `referentiel_niveau_classe` et `starter_welcome`.
- **Dictionnaires de données** : `docs/specs/data-dictionary/` (référentiel, socle
  scolaire, starter welcome).
- **Outillage qualité** : `make check` = 5 portes (pyright strict, ruff, pytest,
  `mkdocs --strict`, `forge project:check`).

La formule de référence du projet :

```text
JSON canonique          = référence structurée de construction / import
Dictionnaire de données = documentation métier enrichie
Base de données         = vérité applicative en fonctionnement
```

---

## 2. Choix du backend : MariaDB (ADR-004)

Parmi les backends Forge (hors SQLite : MariaDB, PostgreSQL alpha, MSSQL alpha),
**MariaDB** a été retenu — seul opt-in **complet**, cohérent avec la règle « 100%
Forge », et largement suffisant pour la charge d'une application pédagogique.

- Décision : [ADR-004](adr/004-backend-base-de-donnees-mariadb.md).
- Le porteur installe l'opt-in `forge-mvc-mariadb` lui-même.

---

## 3. Montée de squelette Forge « en place » (ADR-009)

Le projet suit l'évolution du framework. Une première tentative de migration **par
déplacement de dossiers** a cassé le `.venv` (chemins absolus, non déplaçable) →
**rollback complet**. On a alors défini une méthode **en place** :

- **Décision** : [ADR-009](adr/009-montee-squelette-forge-en-place.md) + procédure
  [Montée de squelette Forge](procedures/montee-squelette-forge.md) (manifeste de
  propriété : fichiers *squelette* vs *projet*).
- **Outillage** créé :
  ```bash
  make skeleton-check REF=../Test    # écarts entre le projet et un forge new neuf
  make forge-upgrade COMMIT=<sha>    # bump du pin + réinstall forcée + make check
  ```
- **Piège documenté** : un pin git à version identique (`1.0.0rc2`) n'est **pas**
  re-fetché par pip → `pip install --force-reinstall --no-deps` (géré par la cible).
- **Structure des routes** (nouveauté ADR-068 côté Forge) : `mvc/routes/` est un
  **package** ; un fichier `mvc/routes/<x>_routes.py` par contrôleur exposant
  `register_<x>_routes(router)`, branché dans `mvc/routes/__init__.py`.

Commits de montée : passage du pin `forge-mvc` `e3197866` → **`f38d5159`** (version
intégrant les correctifs des retours).

---

## 4. Mise en place de MariaDB

### 4.1 Provisioning

`forge db:init` **affiche** le SQL de provisioning (mode par défaut) ; on l'exécute
en session admin (`sudo mariadb`) :

```sql
CREATE DATABASE IF NOT EXISTS `ReferenCiel_Manager`
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
-- compte admin (DDL) et compte applicatif (DML), scellés à la base
CREATE OR REPLACE USER 'app_admin'@'127.0.0.1' IDENTIFIED BY 'app_password';
GRANT ALL PRIVILEGES ON `ReferenCiel_Manager`.* TO 'app_admin'@'127.0.0.1';
CREATE OR REPLACE USER 'app_user'@'127.0.0.1' IDENTIFIED BY 'app_password';
GRANT SELECT, INSERT, UPDATE, DELETE ON `ReferenCiel_Manager`.* TO 'app_user'@'127.0.0.1';
FLUSH PRIVILEGES;
```

Config de connexion dans `env/dev` (gitignoré) : `DB_HOST=127.0.0.1`, `DB_PORT=3306`,
`DB_NAME=ReferenCiel_Manager`, `DB_ADMIN_*`, `DB_APP_*`.

Le backend est déclaré dans `optins/registry.py` : `BACKEND = "mariadb"`.

### 4.2 Table `forge_migrations`

Le registre des migrations n'était pas créé par le provisioning manuel
(→ [retour-003](banc-essai/retour-003-forge-migrations-provisioning-manuel.md),
**corrigé** dans Forge depuis). Contournement historique : création manuelle de la
table via sa DDL exacte.

### 4.3 Connexion SQLTools (piège `localhost` vs `127.0.0.1`)

`localhost` fait passer le driver par le **socket Unix** (compte `@'localhost'`),
`127.0.0.1` force le **TCP** (compte `@'127.0.0.1'`). Nos comptes sont en
`@'127.0.0.1'` → **Server Address = `127.0.0.1`** dans SQLTools (pas `localhost`).
Mot de passe : mode « Ask on connect » ou « Driver Credentials » (le coffre chiffré),
**pas** « plaintext in settings » (car `.vscode/settings.json` est versionné).

---

## 5. Ticket 07 — Tranche verticale Bloc A (walking skeleton)

Objectif : prouver la chaîne complète **contrat → migration → base → CRUD → vue
protégée par l'auth**, sur une entité, puis élargir.

### 5.1 La chaîne d'une entité (le geste de référence)

```bash
forge make:entity <NomPascalCase>        # 1. contrat + modèle (interactif : champs)
# (si on édite le contrat : forge sync:entity <Nom>  → régénère .sql + _base.py)
forge migration:make create_<table> --from-entity <Nom>   # 2. fichier de migration
forge migration:apply                                     # 3. crée la table en base
forge make:crud <Nom>                                     # 4. contrôleur/modèle/vues/routes
# 5. brancher dans mvc/routes/__init__.py :
#    from mvc.routes.<x>_routes import register_<x>_routes
#    register_<x>_routes(router)
make check                                                # 6. 5 portes vertes
```

> **Deux fichiers Python par entité** : `<x>_base.py` (généré, régénéré, **jamais
> édité**) et `<x>.py` (manuel, jumeau, **jamais écrasé** — ta logique métier va ici).

### 5.2 Entité `AnneeScolaire`

Première entité, déroulée de bout en bout (y compris l'auth et le login).

- **Contrat** (`mvc/entities/annee_scolaire/annee_scolaire.json`) :
  `libelle` (string, unique), `date_debut`/`date_fin` (date, nullable),
  `active` (boolean, `default: false` — ajouté à la main puis `sync:entity`),
  timestamps.
- **SQL** (extrait) :
  ```sql
  CREATE TABLE IF NOT EXISTS annee_scolaire (
      Id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
      Libelle VARCHAR(20) NOT NULL,
      UNIQUE KEY uk_annee_scolaire_libelle (Libelle),
      DateDebut DATE NULL, DateFin DATE NULL,
      Active BOOLEAN NOT NULL DEFAULT 0,
      CreatedAt DATETIME NOT NULL, UpdatedAt DATETIME NOT NULL,
      PRIMARY KEY (Id)
  ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
  ```
  > Note : Forge génère les **colonnes en PascalCase** (`Libelle`, `CreatedAt`…).
- **Bugs rencontrés et corrigés** (sur l'ancien `forge-mvc`) :
  - CRUD généré cassé (helper flash manquant, modèle non typé) →
    [retour-005](banc-essai/retour-005-make-crud-code-casse-et-non-conforme.md) ;
  - à l'exécution : login KO (`is_active` int vs bool) et 500 (composant
    `button.html` manquant) →
    [retour-008](banc-essai/retour-008-bugs-runtime-login-mariadb-et-bouton-crud.md).

### 5.3 Authentification & login

```bash
forge auth:init                 # SQL du socle Auth/User dans mvc/models/sql/
# table users via migration versionnée (create_auth_socle) :
#   users, auth_tokens, auth_audit_log, auth_rate_limit_attempts
#   (user_roles/RBAC et auth_mfa_*/MFA OMIS — différés, garde-fou)
forge auth:user:create --email prof@referenciel.local --password-prompt
forge make:auth                 # contrôleur + vue login + auth_routes.py
```

- Routes : `/login` **publiques** (GET+POST), `/logout` protégée ; les routes CRUD
  sont **protégées par défaut** (le cœur redirige les non-authentifiés vers `/login`).
- **Lancer l'app** : `forge run` → serveur **HTTPS** sur `https://127.0.0.1:8000`
  (certificat auto-signé → « continuer » dans le navigateur).
- **Se connecter** : `prof@referenciel.local` / `prof1234`
  (mot de passe posé/réinitialisé via `forge auth:user:password`).
- Résultat : `https://127.0.0.1:8000/annee_scolaire` → login → **liste des années**
  (ex. `2025-2026`). ✅ Walking skeleton complet.

### 5.4 Entité `NiveauClasse`

Deuxième entité, sur le `forge-mvc` **corrigé** (`f38d5159`) : la chaîne complète
est passée **sans un seul correctif manuel** (contraste avec `AnneeScolaire`) —
preuve terrain que les correctifs Forge tiennent.

- Champs : `code` (string, unique), `intitule` (string), timestamps.

### 5.5 Entité `Classe` — relations (⏸️ en pause)

`Classe` référence `AnneeScolaire` et `NiveauClasse` (deux `many_to_one`).

```bash
forge make:entity Classe        # champs propres : code, libelle
forge make:relation             # interactif ×2 :
#   Classe -> AnneeScolaire  (FK annee_scolaire_id, on_delete restrict, index)
#   Classe -> NiveauClasse   (FK niveau_classe_id,  on_delete restrict, index)
forge sync:relations            # régénère mvc/entities/relations.sql (contraintes)
```

**Blocage** : le flux relation ne produit pas de schéma applicable sur MariaDB
(colonne FK non générée ; nom `AnneeScolaireId` PascalCase vs contrainte
`annee_scolaire_id` snake ; type `BIGINT` vs `BIGINT UNSIGNED`). →
[retour-009](banc-essai/retour-009-flux-relation-many-to-one-casse-mariadb.md).
**`Classe` est en pause** (entité décrite, relations déclarées, **pas de table**) en
attendant le correctif Forge, puis on reprendra (migration → table → CRUD).

---

## 6. Rôle de banc d'essai — retours & tickets

L'application **exerce Forge en réel** et remonte chaque friction. Voir la
[vue d'ensemble du banc d'essai](banc-essai/README.md).

- **Retours 001 → 009** : du squelette (001) aux bugs runtime (008) et au flux
  relation (009). Les **retours 001-007 ont été corrigés** dans Forge et **vérifiés**
  sur le terrain.
- **Tickets consolidés** pour l'équipe Forge :
  [ticket-01](banc-essai/ticket-forge-01-retours-terrain-ciel-2tne.md) (résolu),
  [ticket-02](banc-essai/ticket-forge-02-bugs-runtime-tranche-verticale.md),
  [ticket-03](banc-essai/ticket-forge-03-flux-relation-many-to-one.md).
- **Enseignement clé** : `make check` (portes statiques) peut être **vert** alors que
  l'app **plante à l'exécution** (login, rendu, relations). Seul un **parcours
  end-to-end** avec un vrai backend révèle ces bugs.

---

## 7. Décisions prises (réponses aux questions)

Trace des arbitrages structurants (le *pourquoi*) :

- **Backend** = MariaDB (ADR-004).
- **Montée de squelette** = en place, jamais par déplacement de dossier (ADR-009).
- **Auth** = socle de base uniquement ; **RBAC et MFA différés** (opt-ins non
  installés) — sans désactiver l'authentification.
- **`Classe.code`** = unique **dans l'année** (composite `(année, code)`), pas
  globalement — index composite à ajouter plus tard.
- **`on_delete`** des relations = `restrict` (on ne supprime pas une année/niveau qui
  a des classes).
- **Staging git** = explicite (jamais `git add -A`) ; **commit gaté** sur
  `make check && …`.

---

## 8. État courant (au fil de l'eau)

| Élément | État |
|---|---|
| `forge-mvc` | `f38d5159` (correctifs retours 001-008) |
| Tables en base | `annee_scolaire`, `niveau_classe`, `users`, `auth_tokens`, `auth_audit_log`, `auth_rate_limit_attempts`, `forge_migrations` |
| Entités terminées | `AnneeScolaire`, `NiveauClasse` |
| En pause | `Classe` (relations — retour-009) |
| Auth | opérationnelle (login prof, RBAC/MFA différés) |
| Qualité | `make check` vert (5 portes, 12 tests) |

> Reprise prévue : dès le correctif Forge du flux relation, refaire `Classe`
> (make:relation → migration → table `classe` avec FK → CRUD) et marquer retour-009
> résolu.

---

## 9. Commandes de référence

```bash
make setup            # installe tout (prêt au dev)
make check            # 5 portes : pyright, ruff, pytest, mkdocs --strict, project:check
forge run             # lance l'app (https://127.0.0.1:8000)
forge routes:list     # liste les routes (PUBLIC / CSRF)
forge migration:status
make forge-upgrade COMMIT=<sha>   # montée du framework
make skeleton-check REF=../Test   # écarts squelette

# inspecter la base (compte admin, TCP)
mysql -h 127.0.0.1 -u app_admin -papp_password ReferenCiel_Manager -e "SHOW TABLES;"
```
