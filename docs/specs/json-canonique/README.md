# Spécification — JSON canonique

Ce dossier spécifie le **JSON canonique** de RéférenCiel Manager. Il s'agit d'un
document de spécification : il décrit le rôle et les principes du JSON canonique,
en amont de toute production de JSON réel.

> Décision de référence : `docs/adr/002-json-canonique-et-persistance-applicative.md`

## Définition

```text
JSON canonique = référence structurée de construction ou d'import
```

Le JSON canonique est une **forme structurée, stable et vérifiable** d'un objet
métier ou d'un ensemble d'objets métier, dérivée d'une source originelle.

Ce qu'il **est** :

- une référence pour **analyser** les sources ;
- une référence pour **importer** et **construire** initialement les objets
  métier ;
- une base pour **générer ou préremplir** le dictionnaire de données ;
- un support de **validation** de la cohérence métier.

Ce qu'il **n'est pas** :

- ce n'est **pas** un fichier de sauvegarde de l'application ;
- ce n'est **pas** la source de vérité de l'application en fonctionnement
  (cette vérité est en base de données) ;
- ce n'est **pas** un format de parcours plat de type V0 fichier
  (`path.yml`, `palier.yml`, `qcm.yml`, `checklist.yml`).

## Place dans le flux

```text
Sources originelles → JSON canonique → (dictionnaire de données) → construction/import → Base de données
```

- **Sources originelles** : exports CPRO, starters Welcome, référentiels
  officiels, documents pédagogiques, créations professeur.
- **JSON canonique** : la forme structurée intermédiaire, canonique et
  réutilisable.
- **Base de données** : la vérité applicative en fonctionnement, alimentée par
  construction/import à partir du JSON canonique.

## Principes de conception (à détailler)

Ces principes guideront la spécification détaillée, produite dans un ticket
ultérieur :

- **Canonique** : une seule forme de référence par type d'objet métier, quelle
  que soit la source d'origine.
- **Explicite** : structure lisible, champs nommés, pas de convention implicite —
  cohérent avec l'esprit Forge.
- **Vérifiable** : la structure se prête à la validation (schémas, invariants
  métier).
- **Traçable** : le lien avec la source originelle et avec les règles métier
  reste identifiable.

## Portée à ce stade

- Ce README **spécifie le rôle** du JSON canonique ; il ne fournit **pas** encore
  de schéma formel ni d'exemple complet.
- Aucun JSON canonique **CPRO** complet n'est produit à ce stade.
- Aucun JSON canonique **Welcome Réseau** complet n'est produit à ce stade.
- Aucun parcours exemple n'est fourni.

La spécification détaillée (structure, champs, schéma de validation, exemples)
sera ajoutée dans ce dossier selon la roadmap
(`docs/roadmap/roadmap-referenciel-manager.md`).
