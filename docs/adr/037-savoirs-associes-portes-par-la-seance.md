# ADR-037 : Les savoirs associés sont portés par la séance

## Statut

Accepté.

## Date

2026-07-24

## Contexte

Les savoirs associés (ADR-028) étaient portés par la séquence
(`sequence_connaissance`).
Or les documents réels du porteur (ex. « Activité 6 — La tension électrique »)
listent leurs savoirs **par séance** : c'est la séance qui enseigne, la
séquence n'est que la somme de ses séances.
Le projet a par ailleurs déjà fait descendre au niveau séance la durée estimée
et les prérequis, la séquence les **agrégeant** en valeurs dérivées.
Les savoirs suivent la même logique.

## Décision

1. **Nouveau pivot `seance_connaissance`** (miroir de l'ancien pivot séquence) :
   `seance_id` (cascade), `connaissance_id` (cascade), `NiveauCible`, `Statut`,
   `Commentaire`, unique par couple.
   La séance gagne une étape « Savoirs associés » dans son tunnel (entre Fiche
   et Compétences observées), au même maître-détail que l'ancienne étape
   séquence.
2. **La cascade canonique (ADR-036) descend d'un cran, inchangée sur le fond** :
   la séance ne coche des savoirs que sous les **compétences retenues au
   scénario** ; les statuts proposés dépendent de la **nature de la séquence**
   (héritée) ; un savoir n'est **validé** que niveau cible + statut saisis ;
   seuls les statuts **ouvrants** (Apportée/Consolidée en formatif, Mobilisée
   en CCF) ouvrent une compétence.
3. **L'étape « Savoirs associés » de la séquence devient une synthèse
   DÉRIVÉE** (lecture seule) : l'agrégat des savoirs de ses séances, groupé par
   compétence, avec la séance d'origine.
   Cas hors référentiel : les **savoirs libres** (ADR-030) restent saisis au
   niveau séquence, inchangés.
4. **Cycle de statut de la séquence (révision de l'ADR-034)** :
   - **finalise** = titre ET niveau de classe (le cadre est posé) ;
   - **publie** = au moins une séance **ouvrante** (ayant ≥ 1 savoir ouvrant ;
     hors référentiel : au moins une séance) — la garantie de contenu vit là où
     vit le contenu ;
   - **attribue** : inchangé (progressions élève, prime sur tout).
5. **Complétude de la séance** : l'étape Savoirs est complète dès le premier
   savoir ouvrant ; son badge en affiche le compte.
6. **Gardes (ADR-036 §9) re-ciblées** :
   - lier un savoir hors des compétences retenues au scénario : refusé (au
     niveau séance désormais) ;
   - au scénario, décocher un critère observé par une séance : refusé
     (inchangé) ; décocher le dernier critère d'une compétence dont **une
     séance** a des savoirs : refusé (retirer d'abord ces savoirs).
7. **Reprise de données** : les savoirs de séquence existants sont migrés vers
   la **première séance** (ordre le plus bas) de leur séquence ; ceux d'une
   séquence **sans séance** restent dans l'ancien pivot (non affichés,
   récupérables) — aucune perte silencieuse.
   L'ancien pivot `sequence_connaissance` est conservé, déprécié ; sa
   suppression du contrat se fera dans un second temps.

## Conséquences

- La saisie colle aux documents réels : chaque séance déclare ce qu'elle
  enseigne ; la séquence agrège durée, prérequis ET savoirs — un seul patron.
- La cohérence interne de la séance se renforce : on observe des compétences
  dont on enseigne les savoirs dans la même séance.
- Les exports (PDF, Markdown, JSON) présentent l'agrégat au niveau séquence,
  dérivé des séances.
- L'étape séquence perd sa saisie (sauf savoirs libres hors référentiel) : la
  complétude de la séquence ne dépend plus des savoirs, celle de la séance oui.

## Alternatives écartées

- **Garder les savoirs au niveau séquence** : rejeté, contraire aux documents
  réels et au patron d'agrégation du projet.
- **Double saisie (séquence ET séance)** : rejeté, deux sources de vérité.
- **Supprimer immédiatement `sequence_connaissance`** : rejeté, les savoirs des
  séquences sans séance seraient perdus ; dépréciation en deux temps.
