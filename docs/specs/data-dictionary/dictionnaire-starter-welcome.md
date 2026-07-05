# Dictionnaire de données — Starter Welcome

Documentation métier enrichie du domaine **parcours pédagogique** (type
`starter_welcome`), objets **persistés en base** après import du manifeste canonique
(voir le [contrat](../json-canonique/contrat-starter-welcome.md)).

> Mêmes principes que le [dictionnaire référentiel](dictionnaire-referentiel-niveau-classe.md#principes).
> **Définition ≠ exécution** : ce dictionnaire décrit les **contenus définis** ; les
> cases cochées, tentatives et progressions relèvent du **Bloc B** (exécution), non
> couvert ici.

## Contenu par référence

Les contenus lourds (dossiers techniques, activités, images) sont **référencés par
fichier** et stockés via l'opt-in `files` (bundle uploadé, ADR-008), pas embarqués
en base. Les **données structurées** (QCM, checklists) sont persistées.

## Entités

### StarterWelcome

Le parcours réutilisable. Racine du domaine.

| Champ | Type | Oblig. | Description / règle |
|---|---|:--:|---|
| `identifiant` | slug | oui | ex. `welcome-reseau`, **unique** |
| `version` | string | oui | semver |
| `niveau_classe_id` | many_to_one → NiveauClasse | oui | classe visée |
| `titre` | string | oui | ex. « Semaine réseau et virtualisation » |
| `presentation` | text | non | texte d'accueil |
| `activite_glissante` | boolean | oui | chaque élève à son rythme |
| `ordre_impose` | boolean | oui | paliers dans l'ordre |
| `statut` | string | oui | `brouillon` \| `publie` \| `archive` |

### Palier

| Champ | Type | Oblig. | Description / règle |
|---|---|:--:|---|
| `starter_id` | many_to_one → StarterWelcome | oui | parcours parent |
| `ordre` | integer | oui | rang 1..n, **unique et contigu** dans le parcours |
| `titre` | string | oui | |
| `theme` | string | non | |
| `production_attendue` | string | non | ex. « Un câble droit conforme » |
| `dossier_technique_fichier` | string | oui | référence de contenu (bundle) |

### QCM

Un QCM par palier ; porte de passage (validé à 100 % avant l'activité).

| Champ | Type | Oblig. | Description |
|---|---|:--:|---|
| `palier_id` | many_to_one → Palier | oui | palier parent |
| `format_reponse` | text | non | consigne de format |
| `seuil_validation` | string | oui | ex. `100%` |

### QuestionQCM

| Champ | Type | Oblig. | Description / règle |
|---|---|:--:|---|
| `qcm_id` | many_to_one → QCM | oui | QCM parent |
| `numero` | integer | oui | rang, unique dans le QCM |
| `enonce` | text | oui | énoncé |
| `bonne_reponse` | string | oui | `A` \| `B` \| `C` — **doit exister parmi les `ChoixQCM`** |

### ChoixQCM

| Champ | Type | Oblig. | Description |
|---|---|:--:|---|
| `question_id` | many_to_one → QuestionQCM | oui | question parente |
| `lettre` | string | oui | `A` \| `B` \| `C`, unique dans la question |
| `texte` | string | oui | libellé du choix |

### Activite

| Champ | Type | Oblig. | Description |
|---|---|:--:|---|
| `palier_id` | many_to_one → Palier | oui | palier parent |
| `objectif` | text | non | |
| `fichier` | string | non | référence de contenu (bundle) |

### Checklist / SectionChecklist / ItemChecklist

| Entité | Champ | Type | Oblig. | Description |
|---|---|---|:--:|---|
| **Checklist** | `palier_id` | many_to_one → Palier | oui | palier parent |
| | `decision_finale` | json | non | options (validé / à reprendre / correction) |
| **SectionChecklist** | `checklist_id` | many_to_one → Checklist | oui | checklist parente |
| | `numero` | integer | oui | rang |
| | `titre` | string | oui | |
| **ItemChecklist** | `section_id` | many_to_one → SectionChecklist | oui | section parente |
| | `libelle` | text | oui | point à vérifier (définition, pas la case cochée) |

### Image

| Champ | Type | Oblig. | Description |
|---|---|:--:|---|
| `palier_id` | many_to_one → Palier | oui | palier parent |
| `fichier` | string | oui | référence de contenu (bundle) |
| `legende` | string | non | |

### Ressource

| Champ | Type | Oblig. | Description |
|---|---|:--:|---|
| `palier_id` | many_to_one → Palier | oui | palier parent |
| `public` | string | oui | `eleve` \| `professeur` |
| `fichier` | string | oui | référence de contenu (bundle) |

## Relations (récapitulatif)

| Relation | Type Forge | Cardinalité |
|---|---|---|
| StarterWelcome → Palier | many_to_one (inverse) | 1 parcours, n paliers |
| Palier → QCM / Activite / Checklist | many_to_one (inverse) | 1 palier, 0..1 de chaque |
| QCM → QuestionQCM → ChoixQCM | one_to_many | cascade |
| Checklist → SectionChecklist → ItemChecklist | one_to_many | cascade |
| Palier → Image / Ressource | many_to_one (inverse) | 1 palier, n |
| NiveauClasse → StarterWelcome | many_to_one (inverse) | 1 niveau, n parcours |
| **Palier ↔ Competence** (référentiel) | many_to_many (pivot `palier_competence`) — **optionnel** | alignement pédagogique |

## Règles transverses

- **Ordre des paliers** unique et contigu (1..n) dans le parcours.
- **`bonne_reponse` ∈ `ChoixQCM`** de la question (cohérence QCM ↔ corrigé fusionnés).
- **Références de contenu** (`*_fichier`) présentes dans le bundle importé.
- **Versionnement** : un parcours publié et affecté n'est pas modifié librement
  (statut `brouillon`/`publie`/`archive`) ; on affecte une version publiée.
- **Définition ≠ exécution** : les items de checklist sont des **points à vérifier**
  (définition) ; leur validation élève/professeur est de l'**exécution** (Bloc B).
- **Lien référentiel optionnel** : `Palier ↔ Competence` relève du **jugement
  pédagogique** du professeur (non imposé).

## Portée

Couvre la **définition** du parcours (Bloc « définition »). L'**affectation** à une
classe/élève, la **progression**, les **tentatives QCM**, les **checklists remplies**
et les **évaluations** (Bloc B) relèvent de tickets ultérieurs. Contrats d'entité
Forge et migrations à suivre (tickets de programmation, ensemble).
