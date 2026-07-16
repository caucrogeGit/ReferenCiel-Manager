# ADR-025 : Renommage Parcours → Séquence, Palier → Séance

**Statut :** Proposé
**Date :** 2026-07-16

## Contexte

Le modèle pédagogique nomme aujourd'hui **Parcours** et **Palier**.
Dans la sémantique de l'Éducation nationale, ces objets se nomment
**Séquence** et **Séance** (une séquence est une suite de séances).

L'application doit parler le vocabulaire métier des enseignants.
Le décalage actuel gêne la compréhension et la communication avec le terrain.

Le renommage est profond.
Il touche quatre entités (`Parcours`, `Palier`, `ProgressionParcours`,
`ProgressionPalier`), leurs tables, les colonnes de clé étrangère, les pivots,
les routes, la garde RBAC par préfixe, l'espace élève, de nombreux contrôleurs,
modèles et vues, les tests, ainsi que la documentation (dont l'ADR-022).

## Décision

Nous renommons partout **Parcours → Séquence** et **Palier → Séance**.

**Conventions.**

- Les **identifiants** (entités, tables, colonnes, routes, fichiers, symboles de
  code) sont en **ASCII sans accent** : `Sequence`/`sequence`, `Seance`/`seance`.
  Dérivés : `progression_sequence`, `progression_seance`, colonnes `sequence_id`
  et `seance_id`, pivots `scenario_sequence` et `professeur_sequence`, routes
  `/sequence`, `/seance`, `/progression_sequence`, `/progression_seance`, espace
  élève `/mon-parcours` → `/ma-sequence`.
- Les **libellés utilisateur** portent les accents : « Séquence », « Séance »,
  « Ma séquence ».

**Méthode.**

On suit le flux Forge, jamais d'édition à la main du SQL généré.
On modifie le contrat d'entité, on régénère, puis on écrit une migration
idempotente de renommage (`RENAME TABLE`, `ALTER TABLE ... CHANGE ...`).

On procède par **phases**, chacune close par un `make check` vert, dans l'ordre
des dépendances (la feuille d'abord) :

1. `Palier` → `Seance` (table, colonnes FK entrantes, fichiers, routes, RBAC,
   vues, tests).
2. `ProgressionPalier` → `ProgressionSeance`.
3. `Parcours` → `Sequence`.
4. `ProgressionParcours` → `ProgressionSequence`.
5. Pivots (`scenario_parcours`, `professeur_parcours`), espace élève
   (`/mon-parcours` → `/ma-sequence`), navigation et libellés.
6. Documentation : révision de l'ADR-022 (note de renommage), roadmap, specs.

## Conséquences

L'application parle le vocabulaire métier, du modèle jusqu'aux écrans.

Les migrations renomment des tables et des colonnes en production.
Elles sont idempotentes et vérifiées phase par phase.

L'ADR-022 (Parcours objet canonique) reste valable sur le fond.
Il est annoté : l'objet « Parcours » y devient « Séquence », le « Palier »
devient « Séance », sans changer les cardinalités ni la logique.

Les anciennes migrations gardent leurs noms historiques (`*_parcours`,
`*_palier`).
On ne réécrit pas l'histoire ; le renommage vit dans de nouvelles migrations.

## Alternatives écartées

**Libellés utilisateur seulement**, en gardant le modèle interne Parcours/Palier.
Rapide et sans migration, mais installe durablement un écart entre le code et le
métier, source de confusion pour les développements futurs.
Le porteur a choisi l'alignement complet.
