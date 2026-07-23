# ADR-038 : Une étape « Gestion » terminale dans chaque tunnel

## Statut

Accepté.

## Date

2026-07-24.

## Contexte

Les opérations générales sur un objet de conception étaient éparpillées.
La suppression et les exports (PDF, Markdown, JSON) vivaient sur les cartes des
listes ; les ressources du scénario avaient leur propre étape ; l'attribution
d'une séquence passait par un bouton de carte (ADR-035).
Les cartes cumulaient donc l'affichage, la navigation et les commandes, et la
séance n'avait aucun lieu de suppression hors de sa page de liste.
Or la page de liste des séances n'a plus de raison d'être : depuis l'ADR-037 et
l'arbre « Famille pédagogique », la séance est un objet enfant de la séquence,
créé et parcouru depuis l'arbre.

## Décision

1. **Chaque tunnel (scénario, séquence, séance) se termine par une étape
   « Gestion »** qui regroupe toutes les opérations sur l'objet :
   ressources (imports de fichiers), exports, attributions et suppression.
   - Scénario : ressources (absorbe l'ancienne étape « Ressources »), exports
     PDF/Markdown/JSON (réservés aux statuts finalisé/utilisé, ADR-024),
     suppression (verrouillée si utilisé).
   - Séquence : lien vers les attributions (dès publiée, ADR-035), exports
     PDF/Markdown/JSON, suppression (verrouillée si publiée ou attribuée,
     ordre de suppression en infobulle).
   - Séance : suppression (verrouillée si des progressions d'élèves existent) ;
     les exports de séance n'existent pas encore.
2. **« Gestion » est une étape d'outillage, hors complétude.**
   Elle ne compte pas dans la finalisation et ne porte ni coche ni cercle au
   stepper : une icône d'engrenage la distingue (drapeau `outil` dans
   `steps()`).
   Les règles de statut (ADR-034/037) sont inchangées.
3. **Les cartes des listes redeviennent lecture + lien.**
   Cartes scénario et séquence : titre, badges, statut, lien vers le tunnel —
   plus aucune commande (exports, suppression, attribution).
4. **L'entrée « Séances » du menu Conception disparaît.**
   La séance se crée depuis l'arbre « Famille pédagogique », s'ouvre depuis
   l'arbre ou sa séquence, et se supprime dans son étape Gestion.
   Les redirections de repli pointent vers la séquence parente (suppression) ou
   la liste des séquences (création refusée).
   La page `/seance` reste servie mais n'est plus référencée.
5. **Compatibilité d'URL** : `?etape=ressources` (scénario) retombe sur
   `?etape=gestion` ; toute étape inconnue retombe sur la première.

## Conséquences

- Un seul motif à apprendre : tout ce qui agit sur l'objet est au bout de son
  tunnel, gardé par les mêmes règles proactives (boutons neutralisés + ordre de
  suppression en infobulle, gardes serveur conservées).
- Les cartes sont plus lisibles et ne divergent plus du tunnel.
- La suppression d'une séance survit à la disparition de sa page de liste.
- Le pied de tunnel affiche une étape de plus (« Étape n sur n »), sans effet
  sur la complétion ni sur les statuts dérivés.

## Alternatives écartées

- **Garder l'étape « Ressources » du scénario séparée de « Gestion »** :
  distinction contenu/outillage jugée trop subtile ; ressources, imports,
  exports et suppression relèvent tous de la gestion de fichiers et d'objet
  (choix du porteur).
- **Conserver les commandes sur les cartes** : doublon d'interface avec le
  tunnel, cartes surchargées, et incohérence dès que les gardes évoluent.
- **Une page d'administration transversale** : casserait l'unité « un objet,
  un tunnel » posée par les ADR-019/021/032.
