# Les trois projections du référentiel

Le référentiel (ADR-023 : pôles, activités, tâches, compétences, critères,
indicateurs, connaissances) ne se déverse jamais en bloc dans les objets
pédagogiques.
Chaque objet en retient une **projection** : un sous-ensemble choisi par le
professeur, adapté au rôle de l'objet.
Cette page fixe ce vocabulaire commun ; elle décrit l'existant, pas une cible.

| Objet | Axe | Information retenue | Pivots en base |
|---|---|---|---|
| Scénario | évaluatif (« quoi mesurer ») | critères de validation et leurs indicateurs de réussite | `scenario_activite`, `scenario_critere`, `indicateur_reussite` |
| Séquence | contenus (« quoi enseigner ») | synthèse dérivée des savoirs de ses séances ; savoirs libres hors référentiel | `savoir_libre` (dérivation depuis `seance_connaissance`) |
| Séance | opérationnel (« enseigner, observer, positionner ») | savoirs associés (ADR-037), critères observés, puis un niveau de maîtrise par critère et par élève | `seance_connaissance`, `seance_competence`, `seance_critere`, `evaluation_critere`, `indicateur_observe` |

## Le scénario : l'axe évaluatif

Le scénario retient du référentiel des **activités professionnelles** (et leurs
pôles) comme contexte de travail, et surtout des **critères de validation**
avec leurs **indicateurs de réussite**, y compris ceux ajoutés à la main par le
professeur.
C'est l'information produite pour l'aval : ce qui sera mesuré.
Un scénario peut aussi vivre hors référentiel
([ADR-027](../adr/027-scenario-hors-referentiel.md)) ; la projection est alors
vide et le scénario se finalise sur son seul contexte.

## La séquence : l'axe des contenus

Depuis l'[ADR-037](../adr/037-savoirs-associes-portes-par-la-seance.md), les
**savoirs associés sont portés par la séance** (chacun avec son niveau cible et
son statut, [ADR-028](../adr/028-connaissances-associees-ancrage-referentiel.md)) ;
la séquence n'en présente qu'une **synthèse dérivée**, comme pour sa durée et
ses prérequis.
Hors référentiel, les **savoirs libres**
([ADR-030](../adr/030-savoirs-libres-hors-referentiel.md)) restent saisis au
niveau séquence.
C'est ce qui sera enseigné.
Le référentiel lui-même est porté par le scénario appairé
([ADR-029](../adr/029-appairage-scenario-sequence-a-la-creation.md)) : la
séquence y accède par lui, sans double rattachement.

## La séance : l'axe opérationnel, en deux temps

À la **conception**, la séance choisit ses compétences et **critères observés
parmi la liaison du scénario** appairé : l'entonnoir se resserre, sans double
saisie ([ADR-032](../adr/032-modele-seance-tunnel-cascade-evaluation.md)).

À l'**évaluation**, la feuille de positionnement note chaque critère observé,
élève par élève, sur la **grille CIEL des niveaux de maîtrise**
([ADR-033](../adr/033-suivi-evaluation-tableau-de-bord.md)).
Trois règles métier y sont câblées :

1. La donnée métier est le **niveau**, pas la couleur ; le barème de couleur
   (rouge, orange, vert clair, vert foncé) n'est que sa représentation
   visuelle.
2. « Non observé » (gris) est un état **distinct** du rouge : l'élève qui n'a
   pas été placé en situation d'observation n'est pas pénalisé.
3. Les indicateurs cochés ne font que **suggérer** un niveau ; le professeur
   arbitre toujours.

## L'entonnoir d'ensemble

```text
Référentiel (tout)
   └─> Scénario   : critères + indicateurs retenus        (axe évaluatif)
          └─> Séance : critères observés (sous-ensemble)  (axe opérationnel)
                 └─> Évaluation : un niveau par critère et par élève

Séquence : savoirs associés retenus                       (axe des contenus)
```

Les deux axes se rejoignent au scénario, **source canonique des compétences**
([ADR-036](../adr/036-statuts-savoirs-declencheurs-evaluation.md)) : la
séquence n'enseigne (savoirs) que des compétences retenues au scénario, et la
séance observe parmi cette même liaison.
Les statuts des savoirs (Apportée/Consolidée en formatif, Prérequis/Mobilisée
en CCF) qualifient ce que la séquence fait de chaque compétence, et la
suppression d'une compétence du périmètre est gardée dans l'ordre inverse de
la construction (observations, puis savoirs, puis critères).
