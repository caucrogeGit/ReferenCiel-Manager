# Roadmap — RéférenCiel Manager

Trajectoire du projet. Elle fixe l'ordre des grandes étapes ; le détail
d'exécution vit dans les tickets (`docs/tickets/`) et les décisions structurantes
dans les ADR (`docs/adr/`). Le cadre métier est décrit dans
`docs/cadrage/cadre-projet-referenciel-manager.md`, la méthode dans
`docs/cadrage/instructions.md`.

> Une roadmap exhaustive séparée est prévue dans les sources du projet
> (`roadmap-referenciel-manager-exhaustive.md`) ; ce fichier en est la vue courte
> et opérationnelle.

## Principe

On avance par **petits incréments testés**, une responsabilité à la fois, chacun
cadré par un ticket à périmètre explicite. La base de données est la vérité
applicative en fonctionnement ; le JSON canonique est la référence de
construction et d'import ; le dictionnaire de données est la documentation métier
enrichie.

## Ordre de construction (rappel de méthode)

Pour chaque objet métier, on ne part pas des interfaces ni d'un diagramme global,
mais d'une source ou d'une fonctionnalité métier évidente, puis :

```text
source -> provenance -> JSON canonique -> dictionnaire de données -> règles métier
-> cycle de vie -> modèle relationnel -> diagramme de classes -> contrat d'entité Forge
-> migration SQL -> repository -> service -> interface -> tests
```

## Étapes

### Jalon 0 — Cadrage (fait)

- Installer les documents de cadrage et la méthode de travail.
- Acter la décision JSON canonique / persistance (ADR-002).
- Aucun code métier, aucune table, aucune entité.

### Jalon 1 — Chaîne de sources (documentaire)

Installer la chaîne de sources d'un référentiel niveau-classe, sans code
applicatif :

- référentiel officiel Bac Pro CIEL ;
- fichier `.scpro` CPRO et fichier `.odt` exporté ;
- trace de création du JSON canonique (`trace-creation-json-canonique-cpro-2tne.md`) ;
- JSON canonique **CIEL 2TNE** (référentiel niveau-classe) ;
- schéma JSON associé ;
- dictionnaire de données généré ou prérempli.

Reste documentaire : pas de JSON canonique CPRO ou Welcome complet en dehors de
ce qui sert ce jalon, pas de parcours exemple.

### Jalon 2 — Chaîne Scenario (premier objet métier persisté)

Premier objet métier construit de bout en bout :

- dictionnaire de données `Scenario`, règles métier et cycle de vie ;
- modèle relationnel et diagramme de classes `Scenario` ;
- contrat d'entité Forge, migration SQL, repository, service `Scenario` ;
- interface professeur minimale (créer, consulter, modifier, publier) ;
- tests de persistance.

Ne crée pas de parcours fichier comme source principale.

### Jalon 3 — Starters Welcome et parcours

- StarterWelcome (dont Welcome Réseau) et versionnement ;
- Parcours et paliers, avec statuts `brouillon / publie / archive`.

### Jalon 4 — Affectation et exécution élève

- Affectation d'une version publiée à une classe ou à un élève ;
- Progression individuelle ; garantie qu'un parcours affecté ne change pas sous
  les pieds de l'élève.

### Jalon 5 — Contenus de palier

- Dossier technique, QCM de compréhension (le QCM ne valide pas une compétence) ;
- Activité et checklist ; dépôts élève et ressources.

### Jalon 6 — Suivi et évaluation

- Suivi professeur par classe, niveau, parcours, palier et compétence ;
- Évaluation par critères observables dans l'activité ;
- Bilans exploitables par le professeur.

## Transversal (au fil des jalons)

- **Sécurité et rôles** : `eleve`, `professeur`, `administrateur` ; cloisonnement
  des accès ; MFA pour professeur et administrateur.
- **Opt-ins Forge** : appelés via des façades ; le métier ne dépend pas de leur
  détail. Critiques d'abord (facades, rbac, mfa, markdown, fichier, pivot,
  admin), puis utiles (image, qrcode, notification, mail).
- **Versionnement** : appliqué dès qu'un objet publié devient réutilisable.

## Hors trajectoire immédiate

- Réintroduire une V0 fichier ou des `*.yml` de parcours comme base principale.
- Créer un parcours exemple ou les JSON canoniques CPRO / Welcome Réseau complets
  avant que les sources et la spécification ne soient posées.
- Opt-ins repoussés tant qu'ils ne sont pas nécessaires : video, search, cache,
  export/pdf, statistiques avancées, messagerie complète.
