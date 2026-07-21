# ADR-032 : Modèle de la séance — tunnel, sélection en cascade, compétences observées et évaluation

**Statut :** Accepté
**Date :** 2026-07-21

## Contexte

La séance porte déjà ses **attributs** (SEQ-02 : objectif opérationnel, durée,
modalité, conditions de réalisation/validation, remédiation, production
attendue). Deux tables la relient au référentiel — `seance_competence` (avec un
rôle) et `seance_critere` — mais **sans écran**. Il manque aussi le **déroulé
ordonné** de la séance (`ElementSeance`) et l'articulation avec **l'évaluation**.

Un cadrage terrain (exemple CIEL détaillé + règle métier d'évaluation) fixe la
cible : la séance est une **unité de travail** dans laquelle le professeur
observe des critères, et **l'élève ne valide pas directement une compétence** —
le professeur accumule des observations puis arrête un niveau de maîtrise.

Le schéma contient déjà l'essentiel du moteur d'évaluation : `evaluation_activite`
(observation : date, appréciation, professeur, rattachée à `progression_seance`),
`evaluation_critere` (`niveau` + `critere_id`), `progression_seance.statut`,
`bilan_eleve`. Mais l'évaluation est **centrée sur l'activité** (héritage
ADR-022/023), alors que la cible est centrée sur la **séance et la compétence**.

## Décision

**1. La séance est un tunnel** (comme le scénario et la séquence), sans double
saisie : chaque niveau **sélectionne** dans le niveau au-dessus, il ne re-saisit
jamais. Cardinalité **Séquence 1-n Séance**.

**2. Cascade de sélection (source unique : le référentiel).**

```
Référentiel   = compétences, critères, connaissances (source unique)
  Scénario  → SÉLECTIONNE activités + compétences + critères (liaison)
  Séquence  → SÉLECTIONNE les connaissances (savoirs)
  Séance    → SÉLECTIONNE, PARMI la liaison du scénario, les compétences
              qu'elle observe (rôle) + les critères, et définit ses indicateurs
  Évaluation→ référence les critères/indicateurs de la séance
```

**3. La séance pioche dans la liaison du scénario, pas dans tout le référentiel.**
Une séance ne peut choisir que des compétences/critères **déjà liés par le
scénario appairé** (via la séquence 1-1). Cohérence garantie, zéro double saisie.

**4. Compétences observées + indicateurs.** `seance_competence` porte le rôle
(travaillée / évaluée) ; `seance_critere` les critères observés. Les
**indicateurs** de la séance réutilisent `indicateur_reussite` (rattachés au
critère, définis par le professeur, ADR-022) — critères officiels ≠ indicateurs.

**5. `ElementSeance` : déroulé ordonné et polymorphe.** La séance contient des
éléments ordonnés (consigne, vidéo, document, outil interactif, QCM, TP, dépôt,
checklist, validation professeur, synthèse). Selon son type, un élément porte
soit **du contenu libre**, soit **une référence à un objet existant**
(`qcm`, `checklist`, `depot_eleve`, `ressource_dossier`). On ne duplique pas ces
objets. Le schéma précis sera détaillé en phase B.

**6. Règle d'évaluation (métier).** L'élève **ne valide pas** directement une
compétence. Le professeur **observe des critères** et les positionne à un niveau
(non acquis / en cours / acquis / maîtrisé). Chaque évaluation produit une
**observation** (`evaluation_activite` + `evaluation_critere`). Les observations
**s'accumulent** (plusieurs situations, dates, autonomie croissante) ; le
**bilan** de maîtrise (`bilan_eleve`) est **arrêté par le professeur**. **Pas de
validation automatique** par calcul de moyenne : le système propose, le
professeur décide. Le QCM ne valide aucune compétence (il conditionne l'accès).

**7. Réconciliation de l'évaluation (phase C).** L'observation se rattachera à la
**séance / l'élément de séance** (aujourd'hui à l'activité). Les champs manquants
de l'observation seront ajoutés : indicateur utilisé, production/preuve, aide
apportée. Détail et migration en phase C (possiblement un ADR dédié).

## Conséquences

- **Phase A** — tunnel séance + écran de sélection des compétences observées
  (rôle) et critères (parmi la liaison du scénario) + indicateurs. Réutilise le
  patron maître-détail du tunnel. Expose enfin `seance_competence`/`seance_critere`.
- **Phase B** — entité `element_seance` (ordre, type, contenu libre ou référence
  polymorphe vers qcm/checklist/depot/ressource), et son édition ordonnée.
- **Phase C** — alignement du moteur d'évaluation sur la séance/élément +
  enrichissement de l'observation.
- La séance-tunnel remplacera l'accès CRUD gris `/seance` par une expérience
  cohérente avec les autres tunnels (le CRUD peut rester pour la vue liste).
- L'accès aux compétences/critères d'une séance suppose un **scénario appairé
  avec référentiel** ; une séance dont le scénario est hors référentiel n'observe
  pas de critères officiels (cohérent ADR-027 / ADR-030).

## Alternatives écartées

- **La séance pioche dans tout le référentiel** (pas seulement la liaison du
  scénario) : rouvre la double saisie et casse la cohérence scénario↔séance.
  Écartée.
- **Validation automatique d'une compétence** (ex. « deux verts = acquis ») : le
  référentiel CIEL impose un suivi et un bilan arbitré, pas un calcul. Écartée.
- **`ElementSeance` = bloc de texte libre uniquement** : dupliquerait les QCM,
  checklists et dépôts déjà modélisés. Écartée au profit du polymorphisme.
- **Le QCM valide une compétence** : contraire à la règle métier (il vérifie la
  compréhension, il conditionne l'accès). Écartée.

## Amendement (2026-07-21) — grille officielle CIEL

La décision 6 mentionnait des niveaux « non acquis / en cours / acquis /
maîtrisé » : **ce ne sont pas les intitulés officiels**. La grille CIEL retient
**quatre niveaux** (1 Non réalisé 🔴, 2 Réalisation partielle 🟠, 3 Réalisation
satisfaisante 🟩 clair, 4 Réalisation très satisfaisante 🟩 foncé), **plus** un
état **« Non observé »** (gris) **distinct du rouge** — un critère jamais mis en
situation ne pénalise pas l'élève. La donnée métier est le **niveau**, pas la
couleur. Le positionnement peut être **suggéré** à partir du nombre **réel**
d'indicateurs validés (sans seuils figés), mais le professeur **arbitre**.
Référence : `mvc/services/niveaux_maitrise.py`.

## Réalisation (2026-07-21) — feuille de positionnement (phase C)

La décision 7 est réalisée : l'écran de notation `/evaluation/activite/{id}` (un
identifiant de `progression_seance`) devient la **feuille de positionnement**,
centrée sur la séance.

- La grille ne montre plus tout le référentiel mais **ce que la séance observe**
  (`seance_competence` avec son rôle, `seance_critere` avec leurs indicateurs).
- Elle n'exige plus d'`activite` : `evaluation_activite.activite_id` reste NULL.
- Chaque critère se positionne sur la **grille CIEL** (`niveaux_maitrise`) au moyen
  de puces radio sans JavaScript (`static/feuille-evaluation.css`, CSP).
- « Non observé » n'écrit pas de ligne : positionner un critère à ce niveau
  **efface** son `evaluation_critere` (l'élève n'est pas pénalisé).
- L'observation porte désormais la **production/preuve**, l'**aide apportée** et
  l'**appréciation**.
- L'upsert de `evaluation_critere` est explicite (la table n'a pas de clé unique :
  l'ancien `ON DUPLICATE KEY` n'agissait jamais et dupliquait les lignes).

Le vocabulaire persisté passe de l'échelle héritée (« non_atteint … depasse »,
antérieure à l'amendement du jour) aux codes CIEL, par la migration
`20260721230126_remap_niveau_ciel`. Le bilan (`bilan_eleve_model`) agrège
désormais ces mêmes codes. La suggestion automatique (`suggerer_niveau`) attend
les indicateurs réellement validés par l'élève et reste différée.

Le **bilan de maîtrise** applique enfin la décision 6 (« le système propose, le
professeur décide »). Sa création n'est plus un figement automatique de la
moyenne : c'est un écran d'**arbitrage** (`/bilan/preparer?progression_id=<id>`)
où, par compétence, la maîtrise **suggérée** par l'agrégat des critères de la
feuille est **retenue ou ajustée** par le professeur. La synthèse figée conserve
les deux valeurs (`niveau_suggere` et `niveau_arrete`) pour la traçabilité. Le
choix des progressions est limité aux classes du professeur connecté.

## Références

- SEQ-02 (attributs de la séance ; tables `seance_competence`/`seance_critere`).
- `docs/adr/022-parcours-objet-canonique-aplatissement.md` (indicateurs au critère).
- `docs/adr/028-...` / `docs/adr/030-...` (cascade savoirs / hors référentiel).
- Entités d'évaluation existantes : `evaluation_activite`, `evaluation_critere`,
  `progression_seance`, `bilan_eleve`.
