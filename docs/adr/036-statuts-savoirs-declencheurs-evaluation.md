# ADR-036 : Les statuts des savoirs déclenchent la suggestion d'évaluation

## Statut

Accepté (révisé le 2026-07-23 : statuts proposés selon la nature, et
qualification niveau + statut requise pour qu'un savoir compte ; ces deux
points sont implémentés).

## Date

2026-07-23

## Contexte

Le scénario retient des compétences par ses **critères** (axe évaluatif) ; la
séquence colore des compétences par ses **savoirs** (axe des contenus).
Ces deux ensembles peuvent diverger sans que rien ne le montre, et rien ne dit
quand une divergence est un oubli ou un choix pédagogique légitime.
Par ailleurs, les statuts des savoirs (ADR-028 : `prerequis`, `apportee`,
`mobilisee`, `consolidee`) étaient purement descriptifs : affichés et exportés,
jamais consommés par une logique.
Le porteur a formulé la clé de lecture qui relie les deux axes, puis son
inversion en situation certificative (CCF).

## Décision

### 1. Sémantique précise des quatre statuts

Le statut d'un savoir décrit sa place dans la progression, au moment où la
séquence a lieu.
C'est le cycle de vie d'un même savoir à travers les séquences de l'année.

- **Prérequis** : le savoir doit être déjà acquis avant la séquence.
  Il n'est pas enseigné ici ; la séquence s'appuie dessus.
  S'il manque aux élèves, c'est de la remédiation, pas de l'apport.
- **Apportée** : le savoir est introduit pour la première fois dans cette
  séquence ; c'est ici que l'apport de cours a lieu.
- **Mobilisée** : le savoir a été apporté dans une séquence antérieure et il
  est réutilisé ici comme outil, en situation, sans être ré-enseigné.
- **Consolidée** : le savoir, déjà apporté puis mobilisé, est stabilisé et
  approfondi ; c'est typiquement là que le niveau cible monte vers le niveau
  taxonomique officiel.
  Le statut dit où en est le savoir ; le niveau cible dit jusqu'où on le
  pousse.

Un même savoir change donc de statut de séquence en séquence : apporté dans
l'une, mobilisé dans les suivantes, consolidé en fin de parcours, prérequis du
point de vue de toute séquence ultérieure.

### 2. Règle de déclenchement (séquence formative)

Une compétence a vocation à entrer dans la **liaison du scénario** (être
évaluée par ses critères) quand au moins un de ses savoirs est **Apportée** ou
**Consolidée** dans la séquence :

- Apportée : le savoir naît ici, la compétence se positionne ici pour la
  première fois ;
- Consolidée : la maîtrise se confirme ici, souvent avec une exigence
  supérieure.

À l'inverse, **Prérequis** et **Mobilisée** ne déclenchent rien par eux-mêmes :
un savoir prérequis a été évalué avant, un savoir mobilisé n'est qu'un outil au
service du travail de la séquence.

### 3. Inversion en séquence certificative (CCF)

En CCF, rien de nouveau n'est enseigné : les statuts attendus sont
**exclusivement Prérequis et Mobilisée**.

- Un savoir « Apportée » dans une séquence certificative est un **signal
  d'anomalie** (on ne découvre pas une notion le jour de l'épreuve) ;
- « Consolidée » n'y a pas sa place non plus : on certifie, on n'ancre pas ;
- l'évaluation y est pilotée par la **grille de l'épreuve**, et les savoirs
  mobilisés désignent les compétences observées en situation.

| Nature de la séquence | Statuts attendus | Déclencheur d'évaluation |
|---|---|---|
| Formative (cas courant) | Prérequis / Apportée / Consolidée | savoirs Apportée / Consolidée |
| Certificative (CCF) | Prérequis / Mobilisée | la grille de l'épreuve |

### 4. Conséquence de modèle : la nature de la séquence

La règle dépend de la nature de la séquence, que le modèle ne porte pas encore.
Un champ « nature » (formative / certificative) devra être introduit sur la
séquence ; il donnera son sens réel au champ libre `ModalitesEvaluation`
(SEQ-02) et fournira au futur plan de formation ses jalons certificatifs.

### 5. Statuts proposés selon la nature (révision du 2026-07-23)

L'interface ne propose que les statuts qui ont un sens pour la nature de la
séquence, plutôt que de signaler après coup un statut incohérent :

- séquence **formative** : Prérequis, Apportée, Consolidée ;
- séquence **certificative (CCF)** : Prérequis, Mobilisée.

« Mobilisée » devient ainsi propre au certificatif : en formatif, un savoir
réutilisé se déclare Prérequis.
Un statut saisi avant un changement de nature est conservé et signalé
(« hors nature »), jamais effacé.

### 6. Qualification d'un savoir retenu (révision du 2026-07-23)

Un savoir coché n'est **validé** que si son **niveau cible ET son statut** sont
saisis.
Seuls les savoirs validés comptent dans la complétude de l'étape Savoirs
associés (badge et coche) et dans la **finalisation** de la séquence (ADR-034).
Un savoir non qualifié est signalé sur sa ligne (« à compléter »).

### 7. Savoirs ouvrants et finalisation (révision du 2026-07-23)

Parmi les savoirs validés, seuls les savoirs de statut **ouvrant** font qu'une
compétence est réellement **travaillée** (« ouverte ») par la séquence :

- formative : **Apportée** ou **Consolidée** ;
- certificative (CCF) : **Mobilisée**.

Un savoir en simple **Prérequis**, même validé, n'ouvre pas la compétence :
la séquence s'appuie dessus sans la travailler.
Conséquences :

- dans la colonne des compétences de l'étape Savoirs associés, trois états :
  ouverte (orange pastel, bordure gauche), appui seul (neutre, compteur
  conservé), rien de coché (neutre) ;
- la **complétude de l'étape et la finalisation** (ADR-034) exigent au moins
  un savoir ouvrant : une séquence adossée à un référentiel existe pour
  travailler des compétences, formative ou certificative, pas seulement pour
  s'appuyer sur elles ;
- le surlignage orange devient le reflet exact du déclencheur d'évaluation :
  une compétence ouverte côté savoirs a vocation à figurer dans la liaison du
  scénario.

### 8. Le scénario, source canonique des compétences (révision finale du 2026-07-23)

Après essai d'un périmètre dérivé bidirectionnel (union critères ∪ savoirs),
le porteur a tranché pour le modèle **descendant**, plus simple à raisonner :

> Le scénario est la **source canonique** des compétences (critères cochés).
> La séquence n'enseigne (savoirs) que des compétences retenues au scénario.
> La séance observe parmi cette même liaison.

Conséquences :

- dans l'étape Savoirs associés, une compétence non retenue au scénario est
  **inactive** (grisée, non cliquable) ; lier un savoir sous elle est refusé
  côté serveur (« retenez-la d'abord au scénario ») ;
- une compétence dé-retenue au scénario alors que des savoirs y restent est
  marquée « hors scénario » (nettoyage guidé) ;
- l'ordre de travail est assumé : liaison du scénario d'abord, savoirs ensuite,
  observations de séance enfin — l'arbre « Famille pédagogique » rend chaque
  étage accessible en un clic.

### 9. Suppression sévèrement encadrée (révision du 2026-07-23)

La suppression d'une compétence du périmètre passe uniquement par le scénario
(source canonique) et y est gardée, avec message explicite et aucune écriture
en cas de refus :

- décocher un critère **observé par une séance** est refusé (retirer d'abord
  l'observation côté séance) ;
- décocher le **dernier critère d'une compétence dont la séquence a des
  savoirs** est refusé (retirer d'abord ses savoirs côté séquence).

L'ordre de démontage est l'inverse de l'ordre de construction : observations de
séance, puis savoirs de séquence, puis critères du scénario.

### 10. Suggestion, jamais contrainte

Tous les mécanismes issus de cette règle sont des **signaux et des
suggestions**, jamais des blocages :

- côté Savoirs associés : signaler une compétence dont des savoirs sont
  apportés ou consolidés mais qui est absente de la liaison du scénario
  (« enseigné mais non évalué ») ;
- côté Liaison du scénario : signaler une compétence retenue sans aucun savoir
  dans la séquence (« évalué mais rien d'enseigné ici ») ;
- le professeur peut toujours passer outre : évaluer en pure mobilisation est
  légitime (logique d'épreuve), enseigner sans évaluer aussi.

## Conséquences

- Les statuts cessent d'être décoratifs : ils deviennent la **charnière entre
  l'axe des contenus et l'axe évaluatif** (voir la page « Les trois projections
  du référentiel »), dans la philosophie du projet : les décisions dérivent des
  données saisies, jamais l'inverse.
- La divergence scénario/séquence devient **qualifiable** : incohérence
  probable, écart normal, ou anomalie CCF, au lieu d'un simple écart binaire.
- Implémentation réalisée : nature de la séquence (§4-5), qualification et
  savoirs ouvrants (§6-7), scénario source canonique et compétences inactives
  hors périmètre (§8), gardes de suppression au scénario (§9).
  Le choix des critères demeure un geste manuel au scénario (choix pédagogique
  du professeur).
- Cet ADR sert de documentation de référence à ces mécanismes.

## Alternatives écartées

- **Périmètre dérivé bidirectionnel** (critères cochés ∪ compétences ouvertes
  par les savoirs) : implémenté puis retiré le jour même à la demande du
  porteur — cohérent mais trop complexe à raisonner (deux directions, gardes
  croisées) ; le modèle descendant scénario-canonique le remplace.

- **Contrainte stricte** (savoirs cochables uniquement sous les compétences
  retenues au scénario) : rejetée, elle impose un ordre de saisie et interdit
  les cas légitimes « enseigné sans être évalué ici » et l'évaluation en pure
  mobilisation.
- **Laisser la divergence invisible** : rejeté, c'est la source de confusion
  constatée par le porteur.
- **Déclencher l'évaluation sur Mobilisée** : rejeté pour les séquences
  formatives (le savoir mobilisé n'est qu'un outil) ; ce cas est précisément
  celui du CCF, traité par la nature de la séquence.
