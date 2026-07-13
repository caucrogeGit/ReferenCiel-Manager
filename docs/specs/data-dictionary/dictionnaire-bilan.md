# Dictionnaire de données : Bilan élève

Documentation **métier enrichie** du domaine « bilan élève » : le **document de
synthèse** arrêté par le professeur en bout de chaîne pédagogique (ticket 21).
Objet **persisté en base** (ADR-003).

> Place dans la chaîne : `… → progression élève → suivi professeur → évaluation par
> critères → **bilan professeur**`.
> Le bilan **fige** une synthèse des évaluations
> par critères d'un élève, exploitable par le professeur (cadrage §8 : le bilan est
> un objet d'**exécution**, produit par l'usage).

## Principes

- **Nommage** : entités en PascalCase, tables en snake_case (conventions Forge).
- **Types** : types de champ Forge (`string`, `text`, `datetime`, `json`,
  `foreign_key`). PK `Id` gérée par Forge.
- **Base = vérité** (ADR-003). Le bilan est **créé par le professeur**.
- **Document arrêté** : un bilan **fige** un instantané des niveaux atteints
  (champ `synthese`, JSON) au moment de sa création. Un bilan publié ne se
  recalcule pas ; il témoigne de l'état des évaluations à la `date_bilan`.

## Distinction : évaluation ≠ bilan

L'**évaluation** (`EvaluationActivite` / `EvaluationCritere`) enregistre, activité
par activité, le **niveau atteint sur chaque critère observable**. Le **bilan**
en est la **synthèse arrêtée** pour un élève sur un parcours : niveaux agrégés par
compétence + appréciation globale rédigée. Le bilan ne remplace pas l'évaluation :
il la **capitalise**.

## Entité

### BilanEleve

Synthèse d'évaluation d'un élève sur un parcours suivi, arrêtée par un professeur.

| Champ | Type | Oblig. | Description / règle |
|---|---|:--:|---|
| `appreciation_globale` | text | oui | synthèse rédigée du professeur (le cœur du bilan) |
| `statut` | string | oui | cycle de vie : `brouillon` \| `publie` \| `archive` |
| `date_bilan` | datetime | oui | date d'arrêt du bilan |
| `synthese` | json | non | **snapshot figé** des niveaux : par compétence (niveau agrégé) + détail des critères évalués, capturé à la création |
| `eleve_id` | many_to_one → Eleve | oui | l'élève évalué |
| `professeur_id` | many_to_one → Professeur | oui | professeur auteur du bilan |
| `progression_eleve_id` | many_to_one → ProgressionEleve | oui | **périmètre** : le parcours suivi dont on fait le bilan |

## Relations (récapitulatif)

| Relation | Type Forge | Cardinalité |
|---|---|---|
| Eleve → BilanEleve | many_to_one (inverse) | 1 élève, n bilans |
| Professeur → BilanEleve | many_to_one (inverse) | 1 professeur, n bilans |
| ProgressionEleve → BilanEleve | many_to_one (inverse) | 1 progression, n bilans |

## Agrégation (calcul du `synthese`)

Le snapshot est calculé en remontant la chaîne d'évaluation de l'élève sur la
progression : `progression_palier → evaluation_activite → evaluation_critere
(niveau) → critere_observable → competence`.

- **Échelle de niveau** (ordonnée) : `non_atteint` (0) < `partiellement_atteint`
  (1) < `atteint` (2) < `depasse` (3).
- **Niveau d'une compétence** : **moyenne ordinale arrondie** des niveaux de ses
  critères évalués. Une compétence sans critère évalué est marquée `non_evalue`.
- **Maille** : une ligne par compétence (niveau agrégé) + le détail des critères
  (code, libellé, niveau) sous chaque compétence.

## Règles métier & cycle de vie

- **Cycle de vie** : `brouillon` (édition libre) → `publie` (arrêté, exploitable)
  → `archive` (retiré de l'usage courant).
- **Appréciation obligatoire** : un bilan sans `appreciation_globale` n'a pas de sens.
- **Figement** : le `synthese` est capturé à la **création** ; un bilan `publie`
  n'est plus recalculé (témoignage de l'état à la `date_bilan`).
- **Périmètre** : tout bilan référence une `progression_eleve_id` existante ; il
  porte sur un parcours réellement suivi.

## Portée

Ce dictionnaire couvre l'objet **Bilan élève** (ticket 21). En amont : l'**évaluation
par critères** (`EvaluationActivite`, `EvaluationCritere`) et le [**socle
scolaire**](dictionnaire-socle-scolaire.md) (Eleve, Professeur). Le bilan clôt la
chaîne d'exécution du Bloc B.
