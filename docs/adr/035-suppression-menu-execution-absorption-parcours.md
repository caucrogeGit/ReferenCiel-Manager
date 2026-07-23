# ADR-035 : Suppression du menu Exécution, absorbé par les parcours

## Statut

Accepté.

## Date

2026-07-22

## Contexte

Le menu « Exécution » exposait huit CRUD générés (progressions, QCM,
tentatives, checklists, activités, dépôts, évaluations, bilans) : du
back-office brut, redondant avec les parcours dédiés.
L'élève rencontre QCM, checklists et dépôts dans le déroulé de sa séance ;
le professeur observe et évalue via le Suivi et la feuille de positionnement.
Restaient trois capacités sans remplaçant : l'attribution d'une séquence
(seul écran : le CRUD Progressions), la création de QCM et de checklists
(leurs ateliers CRUD), et la rédaction des bilans.

## Décision

1. Le menu « Exécution » est **supprimé**. Les routes CRUD restent montées et
   gardées par le RBAC : elles servent d'ateliers contextuels et de dépannage,
   plus de navigation principale.
2. L'**attribution** se fait depuis la carte de la séquence (bouton
   « Attribuer », visible dès qu'elle est publiée) : page
   `/sequence/{id}/attributions`, attribution par classe entière (idempotente)
   ou par élève, retrait gardé (une attribution avec travail élève commencé ou
   bilan est en RESTRICT au contrat ; bouton neutralisé avec motif).
3. Les éléments de déroulé de type « qcm » et « checklist » **référencent**
   l'objet correspondant de la séance (colonnes `qcm_id`/`checklist_id`,
   désormais pilotées par la carte de l'élément), avec un lien contextuel vers
   l'atelier de création (`/qcm`, `/checklist`).
4. « Bilans élève » devient une entrée directe de la barre latérale, près du
   Suivi, sous sa garde RBAC d'origine (`execution.gerer`).
5. La création de progression reste recalculée dans le statut de la séquence
   (ADR-034) : attribuer fait passer en « attribue », retirer la dernière
   attribution en « publie ».

## Conséquences

- La navigation raconte le métier (concevoir, attribuer, suivre), plus la
  base de données.
- Le professeur attribue là où il voit la séquence, sans connaître la notion
  technique de « progression ».
- Les écrans CRUD retirés du menu restent accessibles par URL pour le
  dépannage ; ils pourront être déclassés un à un quand leurs derniers usages
  auront un équivalent (rédaction des QCM/checklists dans le déroulé,
  notamment : seule la RÉFÉRENCE est câblée, pas la rédaction).

## Alternatives écartées

- Supprimer aussi les routes CRUD : rejeté, la rédaction des QCM et des
  checklists n'a pas encore d'équivalent dans le déroulé.
- Garder le menu en l'état : rejeté, il fait double emploi et expose la
  tuyauterie comme du produit.
- Une entrée « Attributions » globale dans le menu : rejeté, l'attribution
  est un geste sur UNE séquence ; sa place est sur la carte.
