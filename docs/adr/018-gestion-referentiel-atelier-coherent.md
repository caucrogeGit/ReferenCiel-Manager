# ADR-018 : Gérer le référentiel par un atelier cohérent plutôt que des CRUD plats

**Statut :** Accepté
**Date :** 2026-07-14

## Contexte

Un référentiel niveau-classe est une structure arborescente et cohérente, enracinée sur l'entité `referentiel_niveau_classe`.
Il agrège une formation, un niveau de classe, des sources, des pôles d'activité qui portent des activités professionnelles, elles-mêmes des tâches et des résultats attendus, des familles de compétences, des compétences qui portent des critères observables, des connaissances et des indicateurs de réussite.
Il porte aussi des liens transverses, par exemple activité vers compétence et critère vers compétence.

Aujourd'hui, cette structure est exposée dans l'application comme six CRUD plats et indépendants, réunis au menu « Référentiel » : formation, pôle d'activité, activité professionnelle, compétence, critère observable, famille de compétences.
Pour consulter ou corriger un seul référentiel, l'utilisateur navigue entre plusieurs listes séparées, en filtrant mentalement par `referentiel_id`.
La cohérence, pourtant présente en base et dans le JSON canonique, disparaît à l'écran.

Le projet pose déjà que le JSON canonique est la référence structurée de construction (ADR-003), importée comme un tout par `import_referentiel` (ADR-016), la base de données en étant le miroir applicatif.
L'interface d'administration ne reflète pas ce tout : elle l'éclate.

## Décision

1. Introduire une page « atelier référentiel » comme interface principale de gestion d'un référentiel.
   On sélectionne un référentiel, puis on voit son arbre complet en maître-détail : l'arborescence d'un côté (pôles, activités, tâches, résultats, familles, compétences, critères, sources, connaissances, indicateurs), le panneau de détail de l'autre.
   La navigation reste dans le contexte du référentiel sélectionné.

2. Fixer le périmètre d'édition à la consultation et à la correction ciblée.
   L'autorité de construction d'un référentiel reste le JSON canonique (ADR-003) : les évolutions structurelles passent par l'édition du JSON canonique puis un ré-import.
   L'atelier n'est pas un éditeur d'autorité concurrente : il offre une vue cohérente et des corrections ponctuelles, pas la construction d'un référentiel de bout en bout.

3. Reclasser les CRUD générés par entité en surface d'administration bas niveau.
   Ils sortent du menu principal mais restent accessibles, gardés par `referentiel.gerer`, pour la réparation ponctuelle d'une ligne quand l'atelier ne suffit pas.

## Conséquences

- Du code applicatif dédié, un contrôleur et des vues sur mesure, au-dessus des modèles existants, sans nouveau modèle de données ni migration.
- Le menu « Référentiel » pointe vers l'atelier plutôt que vers six listes ; la navigation est simplifiée.
- La cohérence du référentiel devient visible à l'écran, alignée sur le JSON canonique et la base.
- L'édition en application est volontairement limitée, pour ne pas dédoubler l'autorité de construction ; les évolutions lourdes passent par le ré-import.
- Aucune capacité n'est perdue : les CRUD plats restent joignables en administration.
- La régénération d'un CRUD par `make:crud` ne touche pas l'atelier, qui est du code applicatif propre au projet.

## Alternatives écartées

- Garder uniquement les CRUD plats.
  Rejeté : la structure reste éclatée à l'écran, la navigation est fastidieuse, et rien n'empêche une édition hors contexte incohérente, par exemple un critère orphelin ou une hiérarchie cassée.

- Faire de l'atelier un éditeur complet, autorité de construction dans l'application.
  Rejeté : cela entre en tension avec ADR-003, qui fait du JSON canonique la source de construction, et dédoublerait la source de vérité, avec un risque de divergence entre l'application et le JSON canonique.
