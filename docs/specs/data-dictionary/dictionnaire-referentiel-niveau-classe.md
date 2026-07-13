# Dictionnaire de données : Référentiel niveau-classe

Documentation **métier enrichie** du domaine « référentiel niveau-classe » : les
objets **persistés en base** après import d'un JSON canonique
(`type: referentiel_niveau_classe`, voir le
[contrat](../json-canonique/contrat-referentiel-niveau-classe.md) et l'
[ADR-009](../../adr/009-import-json-canonique-par-upload-admin.md)).

> Place dans la chaîne : `JSON canonique → **dictionnaire de données** → modèle
> relationnel → contrats d'entité Forge → base`.
> Le dictionnaire **enrichit** le
> canonique de règles métier ; il ne le recopie pas.

## Principes

- **Nommage** : entités en PascalCase, tables en snake_case (conventions Forge).
- **Types** : types de champ Forge (`string`, `text`, `slug`, `integer`,
  `boolean`, `json`, …). Clé primaire `id` gérée par Forge (non déclarée).
- **Relations** : `many_to_one`, `many_to_many` (via table pivot), conformément à
  Forge (`make:relation`, `make:pivot-crud`).
- **Base = vérité** (ADR-003). Le JSON uploadé est conservé comme trace de
  **provenance** ; les objets vivent en base.
- **Provenance** : chaque élément repris référence sa/ses source(s) (`Source`).

## Entités

### ReferentielNiveauClasse

Le document importé (un référentiel extrait pour une classe). Racine du domaine.

| Champ | Type | Oblig. | Description / règle |
|---|---|:--:|---|
| `identifiant` | slug | oui | id stable (ex. `ciel-2tne`), **unique** |
| `version` | string | oui | semver du document |
| `formation_id` | many_to_one → Formation | oui | formation visée |
| `niveau_classe_id` | many_to_one → NiveauClasse | oui | classe visée |
| `statut` | string | oui | `brouillon` \| `publie` \| `archive` (versionnement, ADR à venir) |
| `importe_le` | datetime | oui | date d'import (auto) |

Règles : `(formation_id, niveau_classe_id, version)` unique.
Un référentiel
**publié** puis affecté n'est pas modifié librement (versionnement).

### Formation

| Champ | Type | Oblig. | Description |
|---|---|:--:|---|
| `code` | string | oui | ex. `BACPRO-CIEL`, **unique** |
| `intitule` | string | oui | libellé complet |

### NiveauClasse

| Champ | Type | Oblig. | Description |
|---|---|:--:|---|
| `code` | string | oui | ex. `2TNE`, **unique** |
| `intitule` | string | oui | libellé |

### PoleActivite

| Champ | Type | Oblig. | Description |
|---|---|:--:|---|
| `referentiel_id` | many_to_one → ReferentielNiveauClasse | oui | rattachement |
| `intitule` | string | oui | ex. « Réalisation et maintenance de produits électroniques » |

Vocabulaire : **pôle d'activités**, jamais « rôle ».

### ActiviteProfessionnelle

| Champ | Type | Oblig. | Description / règle |
|---|---|:--:|---|
| `referentiel_id` | many_to_one → ReferentielNiveauClasse | oui | rattachement |
| `pole_id` | many_to_one → PoleActivite | oui | pôle |
| `code` | string | oui | `E1`/`R2`/`D3` (motif `^[ERD][0-9]+$`), unique dans le référentiel |
| `intitule` | string | oui | libellé |
| `conditions_exercice` | text \| json | non | moyens, autonomie |

Relations : `taches` (one_to_many → Tache), `resultats_attendus`
(one_to_many → ResultatAttendu), `competences` (many_to_many → Competence).

### Tache

| Champ | Type | Oblig. | Description |
|---|---|:--:|---|
| `activite_id` | many_to_one → ActiviteProfessionnelle | oui | activité parente |
| `ordre` | integer | oui | rang |
| `libelle` | text | oui | énoncé de la tâche |

### ResultatAttendu

Lié à une **activité professionnelle** (instructions §7).

| Champ | Type | Oblig. | Description |
|---|---|:--:|---|
| `activite_id` | many_to_one → ActiviteProfessionnelle | oui | activité parente |
| `code` | slug | oui | id local (ex. `ra-e1-1`), unique |
| `libelle` | text | oui | résultat attendu |

### Competence

| Champ | Type | Oblig. | Description / règle |
|---|---|:--:|---|
| `referentiel_id` | many_to_one → ReferentielNiveauClasse | oui | rattachement |
| `code` | string | oui | `C0x` (motif `^C[0-9]{2}$`), unique dans le référentiel |
| `intitule` | string | oui | libellé |

Relations : `connaissances` (one_to_many → Connaissance),
`criteres` (one_to_many → CritereObservable),
`activites` (many_to_many → ActiviteProfessionnelle).

### Connaissance

| Champ | Type | Oblig. | Description |
|---|---|:--:|---|
| `competence_id` | many_to_one → Competence | oui | compétence parente |
| `libelle` | text | oui | connaissance associée |
| `niveau_taxonomique` | integer | non | 1 à 4 |

### CritereObservable

Lié à une **compétence** (instructions §7).

| Champ | Type | Oblig. | Description |
|---|---|:--:|---|
| `competence_id` | many_to_one → Competence | oui | compétence parente |
| `code` | slug | oui | id local (ex. `cr-c03-1`), unique |
| `libelle` | text | oui | critère d'évaluation |

### IndicateurReussite

**Formulation pédagogique exploitable** (instructions §7), dérivée d'un résultat
attendu, d'un critère, ou reformulée.

| Champ | Type | Oblig. | Description |
|---|---|:--:|---|
| `referentiel_id` | many_to_one → ReferentielNiveauClasse | oui | rattachement |
| `code` | slug | oui | id local (ex. `ind-1`), unique |
| `libelle` | text | oui | indicateur exploitable |
| `origine` | string | oui | `resultat_attendu` \| `critere` \| `reformulation` |
| `ref_code` | string | non | code de l'élément d'origine (résultat/critère) |

### FamilleCompetence

Compétence commune de la famille TNE (couche 2ⁿᵈᵉ).

| Champ | Type | Oblig. | Description |
|---|---|:--:|---|
| `referentiel_id` | many_to_one → ReferentielNiveauClasse | oui | rattachement |
| `code` | string | oui | `CCx` (motif `^CC[0-9]$`), unique dans le référentiel |
| `intitule` | string | oui | libellé |

Relation : `competences` (many_to_many → Competence), **mapping famille ↔ CIEL**.

### Source

Provenance d'un référentiel (modèle §8 de la capitalisation).

| Champ | Type | Oblig. | Description |
|---|---|:--:|---|
| `referentiel_id` | many_to_one → ReferentielNiveauClasse | oui | rattachement |
| `source_id` | slug | oui | ex. `referentiel-bac-pro-ciel` |
| `source_type` | string | oui | `pdf_officiel` \| `scpro` \| `odt` \| `starter` |
| `source_fichier` | string | oui | nom/chemin du fichier |
| `source_note` | text | non | commentaire |

## Relations (récapitulatif)

| Relation | Type Forge | Cardinalité |
|---|---|---|
| Formation → ReferentielNiveauClasse | many_to_one (inverse) | 1 formation, n référentiels |
| PoleActivite → ActiviteProfessionnelle | many_to_one (inverse) | 1 pôle, n activités |
| ActiviteProfessionnelle → Tache / ResultatAttendu | one_to_many | 1 activité, n tâches/résultats |
| Competence → Connaissance / CritereObservable | one_to_many | 1 compétence, n connaissances/critères |
| **ActiviteProfessionnelle ↔ Competence** | **many_to_many** (pivot `activite_competence`) | n ↔ n |
| **FamilleCompetence ↔ Competence** | **many_to_many** (pivot `cc_competence`) | n ↔ n |
| ReferentielNiveauClasse → Source | one_to_many | 1 référentiel, n sources |

## Règles transverses

- **Unicité** : codes uniques dans leur périmètre (référentiel).
- **Références résolues** : toute relation pointe vers un objet existant (l'importeur
  refuse un canonique dont une relation est orpheline ; invariants du contrat).
- **Provenance obligatoire** sur les éléments repris (au moins une `Source`).
- **Versionnement** : un référentiel publié et affecté n'est pas modifié librement ;
  on affecte une version publiée (statut `brouillon`/`publie`/`archive`).
- **Vocabulaire** : pôles ≠ rôles ; `resultats_attendus` (activités) ≠ `criteres`
  (compétences) ≠ `indicateurs` (formulation pédagogique).

## Portée

Ce dictionnaire couvre le **domaine référentiel niveau-classe**.
Voir aussi, mêmes
principes : le [dictionnaire du **socle scolaire**](dictionnaire-socle-scolaire.md)
(AnneeScolaire, Classe, Eleve, Professeur, InscriptionEleve…) et celui du
[**Starter Welcome**](dictionnaire-starter-welcome.md) (StarterWelcome, Palier,
QCM, Checklist…).
Les contrats d'entité Forge et migrations en découlent (tickets de
programmation, à faire ensemble).
