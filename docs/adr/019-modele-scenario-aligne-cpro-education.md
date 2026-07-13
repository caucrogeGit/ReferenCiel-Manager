# ADR-019 : Modèle du scénario pédagogique aligné sur cpro-education

**Statut :** Accepté
**Date :** 2026-07-14

## Contexte

cpro-education est l'outil source à partir duquel les référentiels et les scénarios pédagogiques ont été construits.
Il structure un scénario en quatre volets : Titre, Contexte, Liaison avec le référentiel, Ressources.

L'entité `Scenario` de RéférenCiel n'en est aujourd'hui qu'un squelette : titre, intention, objectifs, statut, version, un auteur, un référentiel.
Elle capte l'idée, pas le modèle réel.

Le scénario est le cœur métier de conception de l'application, et il s'appuie sur le référentiel : la section « Liaison avec le référentiel » puise dans l'arbre (pôles, activités, compétences, critères) que l'atelier référentiel affiche (ADR-018).

Distinction d'autorité importante : le référentiel se construit hors application, via le JSON canonique (ADR-003), puis s'importe.
Le scénario, lui, est un contenu rédigé dans l'application par les enseignants.
L'application est donc bien l'outil d'auteur du scénario, sans tension avec ADR-003 qui ne concerne que le référentiel.

## Décision

Faire évoluer l'entité `Scenario` vers le modèle cpro-education, en quatre sections, via les générateurs Forge (`make:entity` pour les champs, `make:relation` pour les liens, migrations).

1. **Titre.**
   Le titre existant est conservé.
   Un indicateur de co-intervention est ajouté (booléen).
   Les co-auteurs deviennent une relation many_to_many `Scenario` vers `Professeur` ; l'auteur existant reste le créateur du scénario.

2. **Contexte.**
   Cinq champs remplacent le couple intention/objectifs du squelette : description et mise en situation professionnelle, problématique métier et missions à réaliser, matériels et logiciels utilisés, liens associés, espaces de formation.

3. **Liaison avec le référentiel.**
   Le scénario cible des activités et des critères du référentiel, à la maille fine, par deux relations many_to_many : `Scenario` vers `ActiviteProfessionnelle` et `Scenario` vers `CritereObservable`.
   Les compétences et les pôles se déduisent des critères et des activités sélectionnés (ce sont leurs parents).
   Les compteurs, le code couleur (compétences communes en rouge) et l'italique des savoir-être sont du rendu, pas du modèle.

4. **Ressources.**
   Un espace de fichiers par scénario, via l'opt-in `forge-mvc-files` déjà installé : dossiers, dépôt de fichiers, quota.

## Conséquences

- Évolution de schéma : nouveaux champs, tables de liaison, migrations ; régénération du CRUD scénario au besoin.
- La section Liaison consomme l'arbre du référentiel (atelier, ADR-018) : le socle sert enfin la conception.
- Construction par incréments, une section à la fois, dans l'ordre du menu cpro : Titre, puis Contexte, puis Liaison, puis Ressources.
- Le scénario est un contenu applicatif vivant : autorité d'auteur dans l'application, révisable, propre à l'enseignant.
- Les Ressources réutilisent `forge-mvc-files`, sans nouveau modèle de fichiers maison.

## Alternatives écartées

- Garder le squelette `Scenario`.
  Rejeté : trop pauvre pour la conception réelle, il ne permet ni la liaison au référentiel ni les ressources.

- Décrire le scénario en JSON canonique, comme le référentiel.
  Rejeté : le scénario est un contenu vivant et propre à l'enseignant, rédigé dans l'application, pas un objet figé importé.

- Ne relier le scénario qu'aux compétences, sans les activités ni les critères.
  Rejeté : cpro cible à la fois les activités et les critères, à la maille fine ; s'en tenir à la compétence perdrait la précision de la liaison.
