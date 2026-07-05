# Instructions de travail — RéférenCiel Manager

Ce document fixe **la méthode de travail** du projet RéférenCiel Manager avant
tout développement applicatif. Il complète — sans le remplacer — le briefing
Forge présent dans `AGENTS.md` et `CLAUDE.md`.

## Nature du projet

RéférenCiel Manager est une **application métier pédagogique persistée**,
construite avec le framework Forge. Elle gère des objets métier (référentiels,
parcours, paliers, évaluations, suivis) qui sont **utilisés, publiés, affectés,
évalués ou suivis** dans l'application en fonctionnement.

Ces objets métier doivent être **persistés en base de données**. La base est la
source de vérité de l'application en marche.

## Les trois niveaux (formule à respecter)

```text
JSON canonique         = référence structurée de construction ou d'import
Dictionnaire de données = documentation métier enrichie et canonique
Base de données         = vérité applicative en fonctionnement
```

- **JSON canonique** — une référence structurée servant à l'analyse, à l'import,
  à la génération documentaire, à la validation et à la construction initiale des
  objets métier. Ce n'est **pas** un simple fichier de sauvegarde, et ce n'est
  **pas** la source de vérité de l'application en marche.
- **Dictionnaire de données** — la documentation métier canonique. Il peut être
  **généré ou prérempli** à partir des JSON canoniques, puis **enrichi** avec les
  règles métier. Ce n'est pas un document purement manuel.
- **Base de données** — la **vérité applicative en fonctionnement**. Tout objet
  métier utilisé, publié, affecté, évalué ou suivi y est persisté.

## Sources originelles admises

Les sources d'où proviennent les JSON canoniques peuvent être :

- des exports CPRO ;
- des starters Welcome ;
- des référentiels officiels ;
- des documents pédagogiques ;
- des créations professeur.

Ces sources peuvent être **transformées** en JSON canoniques métier.

## Discipline de travail

- **Petits incréments, une responsabilité** : on avance par changements ciblés
  et testés, jamais par gros lots.
- **Un ticket = un périmètre** : chaque ticket déclare son périmètre autorisé et
  son hors-périmètre, et s'y tient. Voir `docs/tickets/README.md`.
- **Décision structurante = un ADR** : toute décision d'architecture, de
  convention ou de dépendance est consignée dans `docs/adr/`, au format Forge.
- **Révéler avant de corriger** : on expose la cause d'un comportement surprenant
  avant d'en patcher le symptôme.
- **CLI plutôt qu'à la main** : on s'appuie sur les générateurs Forge plutôt que
  de les contourner.

## Anti-régressions (V0 fichier)

Une ancienne approche « V0 fichier » traitait des fichiers plats (`path.yml`,
`palier.yml`, `qcm.yml`, `checklist.yml`) comme base principale. Cette approche
est **écartée** :

- on ne crée pas de fichier YAML de parcours comme base principale ;
- on ne réintroduit pas la V0 fichier ;
- la base de données reste la vérité applicative en fonctionnement.

## Documents de référence

- `docs/cadrage/cadre-projet-referenciel-manager.md` — le cadre du projet.
- `docs/adr/002-json-canonique-et-persistance-applicative.md` — la décision
  structurante sur le JSON canonique et la persistance.
- `docs/specs/json-canonique/README.md` — la spécification du JSON canonique.
- `docs/roadmap/roadmap-referenciel-manager.md` — la trajectoire du projet.
- `docs/tickets/README.md` — la conduite des tickets.
