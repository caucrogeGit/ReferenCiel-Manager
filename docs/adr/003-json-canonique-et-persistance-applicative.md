# ADR-003 — JSON canonique et persistance applicative

## Statut

Accepté.

## Date

2026-07-05

## Contexte

RéférenCiel Manager est une application métier pédagogique persistée, construite
avec Forge. Ses objets métier (référentiels, parcours, paliers, évaluations,
suivis) proviennent de sources hétérogènes — exports CPRO, starters Welcome,
référentiels officiels, documents pédagogiques, créations professeur.

Une ancienne approche « V0 fichier » traitait des fichiers plats (`path.yml`,
`palier.yml`, `qcm.yml`, `checklist.yml`) comme base principale de
l'application. Cette approche mélange la **référence de construction** et
l'**état en fonctionnement**, ce qui empêche de publier, affecter, évaluer ou
suivre les objets de façon fiable.

Il faut donc trancher, de façon durable, les rôles respectifs du JSON canonique,
du dictionnaire de données et de la base de données.

## Décision

Le projet distingue trois niveaux, aux rôles séparés :

```text
JSON canonique          = référence structurée de construction ou d'import
Dictionnaire de données = documentation métier enrichie et canonique
Base de données         = vérité applicative en fonctionnement
```

1. **JSON canonique = référence structurée de construction ou d'import.**
   Les sources originelles peuvent être transformées en JSON canoniques métier.
   Ces JSON servent à l'analyse, à l'import, à la génération documentaire, à la
   validation et à la construction initiale des objets métier. Le JSON canonique
   **n'est pas** un fichier de sauvegarde, et **n'est pas** la source de vérité
   de l'application en marche.

2. **Dictionnaire de données = documentation métier enrichie et canonique.**
   Il peut être **généré ou prérempli** à partir des JSON canoniques, puis
   **enrichi** avec les règles métier. Il n'est pas purement manuel.

3. **Base de données = vérité applicative en fonctionnement.**
   Tout objet métier utilisé, publié, affecté, évalué ou suivi est **persisté en
   base**. La base — et non les fichiers — est la source de vérité de
   l'application en marche.

4. **La V0 fichier est écartée.** On ne crée pas de fichier YAML de parcours
   (`path.yml`, `palier.yml`, `qcm.yml`, `checklist.yml`) comme base principale,
   et on ne réintroduit pas les fichiers plats comme état applicatif.

## Conséquences

- Les rôles sont sans ambiguïté : le JSON canonique **construit et importe**, la
  base **fait foi** en fonctionnement, le dictionnaire **documente** le sens
  métier.
- La modélisation Forge des objets métier (entités, tables, migrations) découle
  de cette décision : la persistance en base est la cible, conformément à l'esprit
  Forge (SQL visible, requêtes paramétrées, générateurs).
- La construction initiale et les imports restent traçables et rejouables à
  partir des JSON canoniques, sans que ceux-ci deviennent l'état vivant.
- Toute tentation de revenir à une base « fichier » est une régression explicite,
  contraire à cet ADR.

## Alternatives écartées

- **V0 fichier comme base principale** (des `*.yml` de parcours faisant office
  d'état applicatif) : rejetée — elle confond référence et état, et empêche une
  application persistée fiable.
- **Base de données comme unique source de conception** (concevoir directement
  en SQL sans référence structurée amont) : rejetée — on perdrait la traçabilité
  des sources, la génération documentaire et la validation offertes par le JSON
  canonique.
- **Dictionnaire de données purement manuel** : rejeté — coûteux et sujet à la
  dérive ; on préfère le générer/préremplir depuis le JSON canonique puis
  l'enrichir.

## Suite

- Spécifier le JSON canonique : `docs/specs/json-canonique/README.md`.
- Planifier la construction des objets métier persistés : voir la roadmap.
- Numéroter les ADR suivants `003`, `004`, etc. dans `docs/adr/`.
