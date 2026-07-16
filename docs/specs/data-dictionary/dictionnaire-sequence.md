# Dictionnaire de données : Séquence

Documentation **métier enrichie** du domaine « séquence » : ce qui **organise le travail
élève** (instructions §12). Objets **persistés en base** (ADR-003).

> **Modèle canonique aplati (ADR-022).** La **Séquence** est l'objet racine, rattaché
> directement à un **NiveauClasse**. Elle se découpe en **Séances** ; chaque séance porte
> un **DossierTechnique** (ressources + QCM de validation). Un **Scénario** lui est
> apparié (1-1). L'élève progresse via une **ProgressionSequence** (directe, sans
> affectation ni versionnement intermédiaire).

## Principes

- **Nommage / types / relations** : conventions Forge (comme les autres dictionnaires).
- **Base = vérité** (ADR-003). La séquence est **créé par le professeur** (`Professeur n-n
  Séquence`) pour un **NiveauClasse** stable, donc **réutilisable d'une année sur l'autre**.
- **Pas de couche gabarit/versions** : les entités `StarterWelcome`, `VersionStarter`,
  `VersionParcours` et `AffectationParcours` ont été **supprimées** (ADR-022). La publication
  se lit sur le champ `statut` de la séquence ; le suivi élève est porté par
  `ProgressionSequence`.

## Entités

### Séquence

L'**objet canonique** du domaine pédagogique.

| Champ | Type | Oblig. | Description / règle |
|---|---|:--:|---|
| `identifiant` | string | oui | code stable, **unique** (ex. `welcome-reseau`) |
| `titre` | string | oui | nom de la séquence |
| `presentation` | text | non | présentation libre |
| `statut` | string | oui | `brouillon` \| `publie` \| … (publication) |
| `activite_glissante` | boolean | oui | l'ordre des activités n'est pas imposé |
| `ordre_impose` | boolean | oui | les séances doivent être franchis dans l'ordre |
| `niveau_classe_id` | many_to_one → NiveauClasse | oui | niveau visé (stable inter-années) |

### Séance

Le **découpage de la séquence** en étapes. Rattaché **directement** à la séquence.

| Champ | Type | Oblig. | Description / règle |
|---|---|:--:|---|
| `sequence_id` | many_to_one → Séquence | oui | séquence parent |
| `ordre` | integer | oui | rang 1..n, **unique** dans la séquence `(sequence_id, ordre)` |
| `titre` | string | oui | |
| `theme` | string | non | |
| `production_attendue` | string | non | ex. « Un câble droit conforme » |

### DossierTechnique

Le **conteneur de ressources** d'une séance (1-1). Remplace l'ancien champ fichier.

| Champ | Type | Oblig. | Description / règle |
|---|---|:--:|---|
| `titre` | string | oui | |
| `seance_id` | many_to_one → Séance | oui | **unique** (un dossier par séance) |

### RessourceDossier

Une **ressource typée** d'un dossier technique (1-n).

| Champ | Type | Oblig. | Description / règle |
|---|---|:--:|---|
| `type` | string | oui | `markdown` \| `video` \| `audio` \| `lien` |
| `titre` | string | oui | |
| `ordre` | integer | oui | rang d'affichage |
| `contenu` | text | non | markdown (si `type=markdown`) |
| `media_ref` | string | non | référence média (vidéo/audio, opt-ins `forge-mvc-video`/`-audio`) |
| `url` | string | non | lien externe (si `type=lien`) |
| `dossier_technique_id` | many_to_one → DossierTechnique | oui | dossier parent |

### QCM de validation

Le quiz de validation du dossier technique (1-1), à réussir avant l'activité.

| Champ | Type | Oblig. | Description / règle |
|---|---|:--:|---|
| `format_reponse` | text | non | |
| `seuil_validation` | string | oui | seuil de réussite |
| `dossier_technique_id` | many_to_one → DossierTechnique | oui | **unique** (un QCM par dossier) |

### ProgressionSequence

L'**avancement d'un élève sur une séquence** (entité associative). Remplace l'affectation
et l'ancienne `ProgressionEleve`.

| Champ | Type | Oblig. | Description / règle |
|---|---|:--:|---|
| `eleve_id` | many_to_one → Eleve | oui | **unique** `(eleve_id, sequence_id)` |
| `sequence_id` | many_to_one → Séquence | oui | |
| `statut` | string | oui | statut global |
| `date_debut` | date | non | |

## Relations (récapitulatif)

| Relation | Type Forge | Cardinalité |
|---|---|---|
| NiveauClasse → Séquence | many_to_one (inverse) | 1 niveau, n séquence |
| Séquence → Séance | many_to_one (inverse) | 1 séquence, n séances |
| Scénario ↔ Séquence | pivot `scenario_sequence` | **1-1** (unique des deux côtés) |
| Professeur ↔ Séquence | pivot `professeur_sequence` | n-n |
| Séance → DossierTechnique | one_to_one | 1 séance, 1 dossier |
| DossierTechnique → RessourceDossier | many_to_one (inverse) | 1 dossier, n ressources |
| DossierTechnique → QCM | one_to_one | 1 dossier, 1 QCM |
| Élève → ProgressionSequence → Séquence | associative | n-n via ProgressionSequence |
| ProgressionSequence → ProgressionSeance | many_to_one (inverse) | 1 progression, n séances suivis |

## Règles métier & cycle de vie

- **Réutilisation** : une séquence rattachée à un `NiveauClasse` stable se réemploie d'année
  en année (l'année vit sur la `Classe`, pas sur la séquence).
- **Ordre des séances** unique et contigu (1..n) dans la séquence.
- **Publication** : portée par `séquence.statut` (plus de table de versions).
- **Séquence du dossier** : lecture du **DossierTechnique** → réussite du **QCM** → accès
  à l'**Activité** (règle de progression, ADR-021 côté écran).
- **Pas de gel de version** : modifier une séquence affecte les progressions en cours
  (assumé en mono-établissement, ADR-022).

## Portée

Couvre `Séquence`, `Séance`, `DossierTechnique`, `RessourceDossier`, `QCM`,
`ProgressionSequence`. En amont : le [**Scénario**](dictionnaire-scenario.md) (apparié 1-1).
En aval : l'**exécution élève** et le [**Bilan**](dictionnaire-bilan.md) (Bloc B).
