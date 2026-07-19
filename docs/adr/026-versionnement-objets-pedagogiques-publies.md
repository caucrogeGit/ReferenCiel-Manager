# ADR-026 : Versionnement et immutabilité des objets pédagogiques publiés et affectés

**Statut :** Proposé
**Date :** 2026-07-19

Cet ADR est le livrable documentaire du jalon **SEQ-01** de la refonte du domaine
pédagogique (Scénario → Séquence → Séance → Élément de séance). Il ne crée
aucune table ni migration. Il fixe la décision structurante qui conditionne tout
le reste, puis liste les corrections documentaires qu'elle entraîne.

## Contexte

La séquence devient un véritable objet métier et la séance devient librement
composable (à terme via des éléments de séance ordonnés). Cette richesse rend la
définition d'une séance beaucoup plus **mutable** qu'aujourd'hui.

Or trois faits, vérifiés sur le dépôt, se contredisent :

- `instructions.md` (document prioritaire) impose le versionnement (§16, §17,
  §22 : « un parcours publié et affecté ne doit pas changer sous les pieds d'un
  élève » ; statuts brouillon / publié / archivé ; §15 nomme même `VersionScenario`,
  `VersionParcours`, `VersionPalier`…).
- `ADR-022` a **aplati** le modèle et supprimé starter, versions et affectations :
  le versionnement **n'existe plus en base**. Contradiction directe avec
  `instructions.md`.
- La relation scénario ↔ séquence est **1-1** dans le métier : un scénario est
  toujours relié à une séquence et une séquence à un scénario (le professeur relie
  les deux dans un sens ou dans l'autre). Le schéma l'**impose déjà** :
  `scenario_sequence` porte une contrainte `UNIQUE` sur `scenario_id` **et** une
  sur `sequence_id`. Il n'y a donc **pas** de séquence partagée entre scénarios ;
  le risque de versionnement ne vient pas d'un partage, mais de la **modification
  d'une séquence déjà affectée à des élèves en cours de progression**.
- Le **vocabulaire de statut est incohérent** dans le code : le scénario persiste
  `brouillon` / `finalisé` / `utilisé`, tandis que la séquence (fixture
  welcome-reseau), le bilan élève, l'admin et `instructions.md` §17 emploient
  `brouillon` / `publié` / `archivé`. Or « finalisé » (complétude *dérivée*) et
  « publié » (acte délibéré) ne désignent pas la même chose, et « utilisé »
  (conséquence d'une affectation) n'est pas un acte de cycle de vie. À harmoniser.

Point irréversible relevé en revue d'architecture : les tables d'**exécution**
(`tentative_qcm`, `reponse_qcm`, `item_coche`, `depot_eleve`, `evaluation_critere`)
doivent référencer **soit** la définition vivante éditable, **soit** une instance
figée. Ce choix détermine les clés étrangères et **ne se rattrape pas** une fois
des données élèves accumulées. Il doit donc être tranché avant `ElementSeance`.

## Décision (proposée)

**Principe : une séquence est figée à l'affectation. L'exécution élève référence
l'instance figée, jamais la définition vivante éditable.**

1. **Statuts de définition (cycle de vie)** : `brouillon` / `publié` / `archivé` —
   les trois **seuls** statuts *persistés*, alignés sur la séquence, le bilan,
   l'admin et `instructions.md` §17.
   - « **finalisé** » n'est **pas** un statut : c'est un indicateur de
     **complétude dérivé** des données (contexte + activité + critère), qui sert de
     *porte* à la publication (on ne publie que ce qui est complet).
   - « **utilisé** » / « **affecté** » n'est **pas** un statut non plus : l'état
     « gelé » est **dérivé** de l'existence d'une affectation (voir point 2), pas
     stocké comme valeur de `Statut`.
2. **Figeage à l'affectation** : affecter une séquence *publiée* à une classe ou à
   un élève crée un **instantané immuable** de la définition (séquence + séances +
   éléments + QCM + checklist).
3. **Ancrage de l'exécution** : progression, tentatives, réponses, cases cochées,
   dépôts et évaluations référencent l'**instantané affecté** (identifié par
   l'affectation), pas l'objet éditable.
4. **Édition libre du maître** : l'auteur continue d'éditer la définition
   « maître ». Les affectations existantes ne bougent pas ; une nouvelle
   affectation refige à partir de l'état courant.
5. **Mécanisme concret recommandé** : un **instantané par copie** (snapshot),
   plutôt qu'un graphe d'objets `Version*` complet. Plus léger pour l'échelle
   actuelle (une séquence réelle, un auteur), et extensible vers des `Version*`
   explicites si le besoin se prouve.
6. **Cardinalité** : la relation scénario ↔ séquence est **1-1** (déjà imposée en
   base par les contraintes `UNIQUE` sur `scenario_id` et sur `sequence_id` de
   `scenario_sequence`). L'immutabilité est donc portée uniquement par
   l'**affectation** — une séquence est figée quand elle est affectée à des élèves
   — et non par un quelconque partage entre scénarios.

## Conséquences

- Les FK d'exécution pointeront vers l'instance **figée** (identités de
  l'instantané), pas vers `qcm_id` / `seance_id` de la définition vivante.
  → **On ne fige donc pas `tentative_qcm.qcm_id` vers la définition** tant que ce
  choix n'est pas acté (cela corrige une recommandation antérieure de revue).
- Coût : duplication de la définition à chaque affectation. Acceptable à l'échelle
  actuelle ; à surveiller si le volume d'affectations croît.
- **`instructions.md` doit être révisé** pour lever la contradiction : §12 (chaîne
  pédagogique), §15 (liste des objets : remplacer Parcours/Palier/`Version*` par
  Séquence/Séance/instantané), §16 et §17 (aligner sur « figer à l'affectation »),
  §22 (interdits). Sans cette révision, le document prioritaire contredit la
  présente décision.
- **Le scénario devra être harmonisé** (ticket ultérieur, hors SEQ-01/SEQ-02) : il
  persiste aujourd'hui `finalisé` / `utilisé` comme `Statut`. Cible : `finalisé` →
  indicateur de complétude *dérivé* + acte `publié` ; `utilisé` → gel *dérivé* de
  l'affectation. La séquence (déjà en `publié`), le bilan élève et l'admin sont
  déjà alignés sur `brouillon` / `publié` / `archivé`.
- `ElementSeance` (jalon SEQ-03) devra être conçu **« snapshotable »** dès le
  départ (pensé pour la copie immuable).
- `evaluation_critere` portera, dès sa création, un `element_seance_id`
  **nullable** (compatibilité future : savoir un jour quel élément a permis
  l'observation), même inutilisé au premier modèle.

## Alternatives écartées

- **Objets `Version*` explicites** (`VersionSequence`, `VersionSeance`,
  `VersionQcm`), comme le suggère `instructions.md` §15. Plus « propre »
  conceptuellement, mais lourd (tables dédiées + gestion de cycle de versions)
  pour un auteur unique et une séquence. Reporté ; réintroductible si la
  réutilisation entre établissements le justifie.
- **Verrou d'immutabilité à la publication** (aucune édition après publication ;
  cloner pour changer). Plus simple, mais rigide : empêche de corriger une
  coquille sur une séquence publiée mais non encore affectée. Écarté au profit du
  figeage à l'affectation.
- **Statu quo (aucun versionnement, ADR-022)**. Viole `instructions.md` §16/§17 et
  rend tentatives et évaluations ininterprétables dès qu'une séquence affectée est
  modifiée. Écarté.

## Références

- `docs/schema/schema-base-seance.md` — schéma réel du domaine séance.
- `docs/adr/022-parcours-objet-canonique-aplatissement.md` — l'aplatissement à
  l'origine de la contradiction.
- `docs/adr/025-renommage-sequence-seance.md` — vocabulaire Séquence/Séance.
- Jalon suivant : **SEQ-02** (`docs/tickets/seq-02-enrichissement-institutionnel-sequence-seance.md`).
