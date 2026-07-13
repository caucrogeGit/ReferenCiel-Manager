# ADR-012 — Versionnement par entité d'identité + entité de version

**Statut :** Accepté
**Date :** 2026-07-10

## Contexte

Plusieurs objets métier sont **versionnés** (roadmap : référentiel, **starter**,
parcours). Le cycle de vie est `brouillon` → `publie` → `archive`, et « un objet
publié et affecté ne se modifie pas librement » (dictionnaires, [ADR-011](011-importeur-referentiel-upsert-best-effort.md)).

Le ticket 14 (`StarterWelcome` **+ `VersionStarter`**) pose la question : le
versionnement vit-il **en ligne** (champs `version`/`statut` sur l'objet, chaque couple
`identifiant + version` = une ligne) ou via une **entité de version dédiée** ?

Le dictionnaire Starter Welcome (13b) décrivait initialement `StarterWelcome` avec
`version` et `statut` **en ligne**. Le nom explicite `VersionStarter` du ticket 14
indique l'intention d'une entité de version séparée.

## Décision

Adopter le motif **identité + versions** :

- une **entité d'identité** porte ce qui est **stable** dans le temps (identifiant
  unique, titre, rattachements structurants) ;
- une **entité de version** (`Version<Objet>`) porte ce qui **varie d'une version à
  l'autre** (numéro de `version`, `statut` du cycle de vie, options et **contenu**), et
  référence son identité en `many_to_one` (1 identité → n versions) ;
- unicité **`(<objet>_id, version)`** sur la version.

Application au ticket 14 :

- **`StarterWelcome`** (identité) : `identifiant` (unique), `titre`, `presentation`,
  `niveau_classe_id` (→ NiveauClasse).
- **`VersionStarter`** (version) : `version` (semver), `statut`
  (`brouillon`/`publie`/`archive`), `activite_glissante`, `ordre_impose`, `starter_id`
  (→ StarterWelcome) ; unique `(starter_id, version)`.

Les **contenus versionnés** (paliers, QCM, checklists — tickets ultérieurs) se
rattacheront à une **`VersionStarter`**, pas à l'identité : deux versions d'un même
starter ont des contenus différents.

## Conséquences

- **Positif** : identité stable (l'`identifiant` ne bouge pas) ; historique des versions
  conservé ; une version `publie` reste figée pendant qu'une nouvelle `brouillon` se
  prépare ; le cycle de vie porte sur la **version**, pas sur l'identité.
- **Motif réutilisable** : `Parcours` + `VersionParcours` (ticket 15) suivra le même
  patron.
- **Affine le dictionnaire** : le dictionnaire Starter Welcome (13b) est mis à jour — les
  champs `version`/`statut`/organisation migrent de `StarterWelcome` vers `VersionStarter`.
- **Coût** : une jointure de plus (identité ↔ version) et le choix, à l'usage, de la
  version « courante » d'un starter (règle métier : au plus une `publie` à la fois — à
  border plus tard).

## Alternatives écartées

- **Version en ligne** (une seule entité, `version`+`statut` inline) : plus simple, mais
  mélange identité et version, ne conserve pas proprement l'historique, et ne remplit pas
  l'intention `+VersionStarter` du ticket 14.
- **Versionnement applicatif hors base** (fichiers/snapshots) : contraire à « base =
  vérité » (ADR-003).
