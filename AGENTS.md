<!-- PRIORITÉ REFERENCIEL-MANAGER -->
# Priorité projet — RéférenCiel Manager

> Ce bloc a la **priorité** sur le briefing Forge ci-dessous en cas de tension.
> Il ne le remplace pas : le briefing Forge reste en vigueur.

RéférenCiel Manager est une **application métier pédagogique persistée** construite
avec Forge. Trois niveaux, aux rôles distincts :

```text
JSON canonique          = référence structurée de construction ou d'import
Dictionnaire de données = documentation métier enrichie et canonique
Base de données         = vérité applicative en fonctionnement
```

- Le **JSON canonique** sert à analyser, importer, générer la documentation,
  valider et construire les objets métier. Ce n'est **pas** un fichier de
  sauvegarde, ni la vérité de l'application en marche.
- Le **dictionnaire de données** est généré/prérempli depuis les JSON canoniques,
  puis enrichi des règles métier. Il n'est pas purement manuel.
- La **base de données** est la **vérité applicative en fonctionnement** : tout
  objet métier utilisé, publié, affecté, évalué ou suivi y est persisté.
- **Pas de V0 fichier** : aucun `path.yml`, `palier.yml`, `qcm.yml` ou
  `checklist.yml` comme base principale.

Documents de cadrage : `docs/cadrage/instructions.md`,
`docs/cadrage/cadre-projet-referenciel-manager.md`,
`docs/adr/002-json-canonique-et-persistance-applicative.md`,
`docs/specs/json-canonique/README.md`,
`docs/roadmap/roadmap-referenciel-manager.md`, `docs/tickets/README.md`.
<!-- FIN PRIORITÉ REFERENCIEL-MANAGER -->

# Forge — briefing agent (application)

Tu travailles sur une **application** construite avec le framework Python Forge.
Tu ne développes pas Forge lui-même : Forge est une dépendance installée
(`forge-mvc`), pilotée par la commande `forge`.

Objectif : produire du code applicatif clair, testable et conforme aux
conventions de Forge, en t'appuyant sur ses générateurs plutôt qu'en les
contournant.

## Esprit Forge

- Explicite plutôt que magique : pas de comportement caché.
- SQL visible : pas d'ORM ; les requêtes sont écrites et paramétrées.
- Sécurisé par défaut : authentification, CSRF et sessions sont déjà en place.
- Une seule façon officielle de faire chaque chose : suis la convention.

## Où vivent les choses

- `mvc/entities/<entite>/<entite>.json` : contrat d'entité (source de vérité).
- `mvc/entities/<entite>/<entite>.sql` : schéma SQL généré.
- `mvc/models/` et `mvc/controllers/` : modèles et contrôleurs.
- `mvc/views/` : templates Jinja.
- `mvc/routes.py` : déclaration explicite des routes.
- `config.py`, `env/` : configuration et environnements (secrets hors du dépôt).
- `schemas/` : schémas JSON pour la validation et l'autocomplétion.

## Conventions

- **Entités** : décrites par un contrat JSON (`schema_version` 1.0, `name` en
  PascalCase, `table`, `fields`). On modifie le contrat, puis on régénère ;
  on ne bricole pas le SQL à la main.
- **Routes** (ADR-029) : chemin `/<controleur>/<methode>` (méthode `index` au
  chemin nu), nom `<controleur>-<methode>` (avec un tiret). Les routes sont
  montées explicitement dans `mvc/routes.py`.
- **Base de données** : via `core.database.db` (`fetch_all`, `fetch_one`,
  `execute`, `insert`), avec des paramètres `?`. Jamais de valeur interpolée
  directement dans le SQL.
- **Sécurité** : les formulaires incluent le jeton CSRF ; les routes protégées
  exigent une session authentifiée. Ne désactive pas ces protections.

## Utilise la CLI plutôt que d'écrire à la main

- `forge make:entity`, `forge make:crud`, `forge make:relation` : entités et CRUD.
- `forge make:public-page|public-list|public-show|public-form` : pages publiques.
- `forge db:init`, `forge db:apply`, `forge migration:make|apply|status` : base.
- `forge entity:validate`, `forge schema:doctor` : cohérence des contrats.
- `forge auth:init`, `forge opt-in:install|enable <module>` : auth et opt-ins.
- `forge run` : lancer l'application ; `forge routes:list` : voir les routes.

## Règle d'or : préserver le code utilisateur

Forge fonctionne en trois modes : il **génère** des fichiers nouveaux
(write-if-new), il **affiche** du code à copier, il **lit** pour analyser.
Il ne réécrit jamais silencieusement un fichier existant.

- Les fichiers `*_base.py` sont **régénérables** : ne les édite pas, ils seront
  écrasés. Mets ta logique dans le fichier manuel jumeau (sans `_base`).
- Ne modifie pas un fichier généré pour contourner une limite : ajuste le
  contrat ou ajoute du code dans la couche prévue.

## Méthode de travail (la discipline de Forge)

Forge a été construit avec une discipline que tu gagnes à reprendre dans ton app :

- **Petits incréments, une responsabilité** : avance par changements ciblés et
  testés, pas par gros lots.
- **Décisions structurantes = un ADR** : quand tu prends une décision
  d'architecture, de convention ou de dépendance qui engage le projet dans la
  durée, consigne-la dans `docs/adr/<numero>-<sujet>.md`, au format Forge
  (Statut, Date, Contexte, Décision, Conséquences, Alternatives écartées).
  L'ADR garde la trace du *pourquoi*, pas seulement du *quoi*. Un premier ADR
  d'exemple est déjà fourni : `docs/adr/001-adopter-forge.md` ; numérote les
  suivants `002`, `003`, etc.
- **Révéler avant de corriger** : si un comportement surprend, comprends et
  expose la cause avant de patcher le symptôme.

## À éviter

- Ajouter un ORM ou une couche d'abstraction qui masque le SQL.
- Écrire des requêtes non paramétrées (risque d'injection).
- Contourner les générateurs en recopiant du code à la main de façon divergente.
- Désactiver CSRF, l'authentification ou la validation pour aller plus vite.
- Mettre des secrets dans le dépôt (utilise `env/`).

## Valider avant de livrer

- `python -m pytest` : la suite de tests.
- `forge doctor` : diagnostic du projet (structure, base, sécurité).
- `ruff check .` : style et erreurs.
- `mkdocs build --strict` : si le projet a une documentation.

## Aller plus loin

La documentation complète de Forge (guide, conventions, référence, ADR) est
publiée sur https://forgemvc.com/docs/forge/.

---

Ce fichier a été généré par Forge (`forge new` ou `forge agents:init`).
Tu peux l'adapter à ton projet ; `forge agents:init --check` signale s'il a
divergé de la version de référence de Forge installée.
