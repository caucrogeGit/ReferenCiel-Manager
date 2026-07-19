# Ticket SEQ-02 — Enrichissement institutionnel de la séquence et de la séance

Jalon de la refonte pédagogique (Scénario → Séquence → Séance → Élément de séance).
Précédé de **SEQ-01** (`docs/adr/026-versionnement-objets-pedagogiques-publies.md`).
Suivi de **SEQ-03** (élément de séance, hors périmètre ici).

Ce ticket vise **80 % de la valeur institutionnelle pour un risque faible** :
rendre une séquence et une séance conformes au formalisme de l'Éducation
nationale (vademecum voie professionnelle) par **ajout de champs et de relations
au référentiel**, sans toucher à la composition libre ni à l'exécution élève.

## Objectif

Permettre à une séquence et à une séance de porter les informations
institutionnelles attendues (contexte professionnel, problématique, objectifs,
prérequis, positionnement, savoirs associés, compétences, critères, modalités
d'évaluation), afin que la séquence Welcome Réseau devienne **défendable devant
une inspection** — sans modifier la façon dont une séance est composée.

## Périmètre autorisé

- **Dictionnaire de données** (`docs/specs/data-dictionary`) : entrées enrichies
  `Sequence` et `Seance` (sens métier des champs, cardinalités, règles de
  validation et de visibilité).
- **Décision de frontière `Scenario` / `Sequence`** : le scénario porte déjà
  `Intention`, `Objectifs`, `DescriptionContexte`, `Problematique`. Il faut
  répartir explicitement ce qui reste au scénario (cadre global, référentiel,
  finalité) et ce qui va à la séquence (problématique *spécifique*, objectif de
  séquence, positionnement), **sans dupliquer de colonne**.
- **Champs additifs sur `sequence`** (uniquement ceux non déjà portés par
  `scenario`) : `ContexteProfessionnel`, `ObjectifsGeneraux`, `Prerequis`,
  `PositionnementProgression`, `DureeEstimee`, `ModalitesEvaluation`.
- **Champs additifs sur `seance`** : `ObjectifOperationnel`, `DescriptionGenerale`,
  `DureeEstimeeMinutes`, `ModalitePedagogique`, `ConditionRealisation`,
  `ConditionValidation`, `Remediation`. (`ProductionAttendue` et `Theme` existent
  déjà et sont conservés.)
- **Relations n-n vers le référentiel** (tables pivots) : `sequence_competence`,
  `sequence_critere`, `sequence_savoir_associe` ; `seance_competence` (avec un
  rôle explicite `travaillee` / `observee` / `evaluee`) et `seance_critere`.
- **Migration additive** via le flux Forge (modifier le contrat, régénérer,
  `make:relation` pour les pivots). Aucune suppression ni renommage de colonne
  existante.

## Hors périmètre

- `ElementSeance` et la composition libre de la séance (→ **SEQ-03**).
- `OutilPedagogique` / catalogue d'outils (→ `docs/tickets/ticket-22-bac-a-sable-outils-pedagogiques.md`).
- Toute modification des tables d'**exécution** (`progression_sequence`,
  `progression_seance`, `tentative_qcm`, `reponse_qcm`, `item_coche`,
  `depot_eleve`, `evaluation_activite`, `evaluation_critere`).
- Le **versionnement / l'immutabilité** (traités par SEQ-01 / ADR-026).
- Les **interfaces** d'édition des nouveaux champs (ticket ultérieur).

## Boucle de travail obligatoire

1. Rédiger/enrichir le dictionnaire `Sequence` et `Seance` (sens, cardinalités,
   règles) — **avant** tout champ.
2. Trancher la frontière `Scenario` / `Sequence` : tableau « champ → objet
   porteur », garantissant zéro colonne dupliquée.
3. Déduire les champs et les pivots **du dictionnaire** (pas l'inverse).
4. Modifier les contrats d'entité Forge (`sequence.json`, `seance.json`) et créer
   les entités pivots via `forge make:entity` / `forge make:relation`.
5. Régénérer, produire la **migration additive**, puis `forge entity:validate` et
   `forge schema:doctor`.
6. `make check` vert.
7. Vérifier sur la séquence **Welcome Réseau** que les nouveaux champs se peuplent
   (fixtures ou import), sans toucher à sa composition.

## Test prémortem

- **Duplication** : `ContexteProfessionnel`/`Problematique`/`Objectifs` finissent
  à la fois sur `scenario` et `sequence` → divergence des deux copies.
  *Mitigation* : décision de frontière (étape 2) **avant** d'ajouter un champ.
- **Sur-conception** : ajouter des champs dont Welcome ne se sert pas.
  *Mitigation* : ne retenir que les champs présents dans le vademecum **et** utiles
  à Welcome.
- **Compétences/critères modélisés en colonnes** au lieu de pivots n-n.
  *Mitigation* : ce sont des relations ; oublier le rôle
  (`travaillee`/`observee`/`evaluee`) sur `seance_competence` casserait le suivi.
- **Rupture d'exécution** : toucher par erreur une table `progression_*` ou
  `evaluation_*`. *Mitigation* : périmètre strictement additif côté définition.

## Critères de validation

- Dictionnaire `Sequence` et `Seance` à jour ; frontière `Scenario`/`Sequence`
  explicitée, **aucune colonne dupliquée**.
- Contrats modifiés et **migration additive** appliquée ; `entity:validate` et
  `schema:doctor` sans erreur.
- `make check` vert (pyright, ruff, tests, `mkdocs build --strict`).
- La séquence Welcome peut porter contexte, problématique, objectifs, prérequis,
  compétences, critères, savoirs associés et modalités d'évaluation **sans**
  modification de sa composition.
- **Aucune** table d'exécution modifiée.
