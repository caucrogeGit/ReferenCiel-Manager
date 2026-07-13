# Dictionnaire de données : Scénario pédagogique

Documentation **métier enrichie** du domaine « scénario pédagogique » : le premier
**objet métier persisté** créé par le professeur (chaîne Scenario, roadmap jalon 2,
instructions §12-14).
Objets **persistés en base** (ADR-003).

> Place dans la chaîne pédagogique : `référentiel niveau-classe → compétences /
> critères observables → **scénario pédagogique** → starter Welcome → parcours →
> affectation → …`.
> Le scénario **définit l'intention** ; le starter la rend
> réutilisable ; le parcours organise le travail élève.

## Principes

- **Nommage** : entités en PascalCase, tables en snake_case (conventions Forge).
- **Types** : types de champ Forge (`string`, `text`, `foreign_key`, …). PK `Id` gérée
  par Forge.
- **Relations** : `many_to_one` et `many_to_many` (via table pivot), conformément à Forge.
- **Base = vérité** (ADR-003). Le scénario est **créé par le professeur** via une
  interface (ou importé depuis une source / un JSON canonique), pas en dur dans le dépôt.
- **Distinction** : le scénario **définit l'intention** ; il ne contient pas le travail
  élève (paliers, activités, checklists) ; cela relève du parcours/starter en aval.

## Entité

### Scenario

L'intention pédagogique d'un professeur, adossée à un référentiel niveau-classe et
ciblant des compétences (et leurs critères observables).

| Champ | Type | Oblig. | Description / règle |
|---|---|:--:|---|
| `titre` | string | oui | nom court du scénario |
| `intention` | text | oui | **l'intention pédagogique** (le cœur du scénario) |
| `objectifs` | text | non | objectifs pédagogiques visés (facultatif, complète l'intention) |
| `statut` | string | oui | cycle de vie : `brouillon` \| `publie` \| `archive` |
| `version` | string | oui | versionnement (semver ou libre) |
| `referentiel_id` | many_to_one → ReferentielNiveauClasse | oui | référentiel-source (cadre) |
| `auteur_id` | many_to_one → Professeur | oui | professeur auteur |

Relations :

- `competences` (**many_to_many** → Competence, pivot `scenario_competence`) : les
  **compétences visées** par l'intention ;
- `criteres` (**many_to_many** → CritereObservable, pivot `scenario_critere`) : les
  **critères observables** retenus pour l'évaluation (l'évaluation se fait dans
  l'activité, à partir de critères, instructions §12).

## Relations (récapitulatif)

| Relation | Type Forge | Cardinalité |
|---|---|---|
| ReferentielNiveauClasse → Scenario | many_to_one (inverse) | 1 référentiel, n scénarios |
| Professeur → Scenario | many_to_one (inverse) | 1 professeur, n scénarios |
| **Scenario ↔ Competence** | many_to_many (pivot `scenario_competence`) | n ↔ n |
| **Scenario ↔ CritereObservable** | many_to_many (pivot `scenario_critere`) | n ↔ n |

## Règles métier & cycle de vie

- **Cycle de vie** : `brouillon` (édition libre) → `publie` (réutilisable, base d'un
  starter/parcours) → `archive` (retiré de l'usage courant). Un scénario **publié** ne se
  modifie pas librement (versionnement à venir, cohérent avec le référentiel).
- **Intention obligatoire** : un scénario sans `intention` n'a pas de sens.
- **Ciblage** : un scénario **devrait** cibler au moins une compétence (règle métier ;
  non contrainte au niveau du schéma pour le m2m).
- **Provenance / cadre** : tout scénario référence un `referentiel_id` existant ; il
  s'inscrit dans un référentiel niveau-classe.
- **Le QCM ne valide pas une compétence** ; le scénario porte l'intention, l'évaluation
  des compétences se fait plus loin, dans l'activité, via les critères observables.

## Portée

Ce dictionnaire couvre l'objet **Scénario pédagogique** (chaîne Scenario, tickets 12-13).
En aval : **Starter Welcome** ([dictionnaire dédié](dictionnaire-starter-welcome.md) :
Palier, QCM, Checklist…) et le **parcours** (exécution élève, Bloc B).
En amont : le
[**référentiel niveau-classe**](dictionnaire-referentiel-niveau-classe.md) (compétences,
critères) et le [**socle scolaire**](dictionnaire-socle-scolaire.md) (Professeur, Classe…).
