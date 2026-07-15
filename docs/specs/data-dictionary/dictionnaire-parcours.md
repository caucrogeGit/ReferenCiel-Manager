# Dictionnaire de données : Parcours

Documentation **métier enrichie** du domaine « parcours » : ce qui **organise le travail
élève** (instructions §12). Objets **persistés en base** (ADR-003).

> **Modèle canonique aplati (ADR-022).** Le **Parcours** est l'objet racine, rattaché
> directement à un **NiveauClasse**. Il se découpe en **Paliers** ; chaque palier porte
> un **DossierTechnique** (ressources + QCM de validation). Un **Scénario** lui est
> apparié (1-1). L'élève progresse via une **ProgressionParcours** (directe, sans
> affectation ni versionnement intermédiaire).

## Principes

- **Nommage / types / relations** : conventions Forge (comme les autres dictionnaires).
- **Base = vérité** (ADR-003). Le parcours est **créé par le professeur** (`Professeur n-n
  Parcours`) pour un **NiveauClasse** stable, donc **réutilisable d'une année sur l'autre**.
- **Pas de couche gabarit/versions** : les entités `StarterWelcome`, `VersionStarter`,
  `VersionParcours` et `AffectationParcours` ont été **supprimées** (ADR-022). La publication
  se lit sur le champ `statut` du parcours ; le suivi élève est porté par
  `ProgressionParcours`.

## Entités

### Parcours

L'**objet canonique** du domaine pédagogique.

| Champ | Type | Oblig. | Description / règle |
|---|---|:--:|---|
| `identifiant` | string | oui | code stable, **unique** (ex. `welcome-reseau`) |
| `titre` | string | oui | nom du parcours |
| `presentation` | text | non | présentation libre |
| `statut` | string | oui | `brouillon` \| `publie` \| … (publication) |
| `activite_glissante` | boolean | oui | l'ordre des activités n'est pas imposé |
| `ordre_impose` | boolean | oui | les paliers doivent être franchis dans l'ordre |
| `niveau_classe_id` | many_to_one → NiveauClasse | oui | niveau visé (stable inter-années) |

### Palier

Le **découpage du parcours** en étapes. Rattaché **directement** au parcours.

| Champ | Type | Oblig. | Description / règle |
|---|---|:--:|---|
| `parcours_id` | many_to_one → Parcours | oui | parcours parent |
| `ordre` | integer | oui | rang 1..n, **unique** dans le parcours `(parcours_id, ordre)` |
| `titre` | string | oui | |
| `theme` | string | non | |
| `production_attendue` | string | non | ex. « Un câble droit conforme » |

### DossierTechnique

Le **conteneur de ressources** d'un palier (1-1). Remplace l'ancien champ fichier.

| Champ | Type | Oblig. | Description / règle |
|---|---|:--:|---|
| `titre` | string | oui | |
| `palier_id` | many_to_one → Palier | oui | **unique** (un dossier par palier) |

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

### ProgressionParcours

L'**avancement d'un élève sur un parcours** (entité associative). Remplace l'affectation
et l'ancienne `ProgressionEleve`.

| Champ | Type | Oblig. | Description / règle |
|---|---|:--:|---|
| `eleve_id` | many_to_one → Eleve | oui | **unique** `(eleve_id, parcours_id)` |
| `parcours_id` | many_to_one → Parcours | oui | |
| `statut` | string | oui | statut global |
| `date_debut` | date | non | |

## Relations (récapitulatif)

| Relation | Type Forge | Cardinalité |
|---|---|---|
| NiveauClasse → Parcours | many_to_one (inverse) | 1 niveau, n parcours |
| Parcours → Palier | many_to_one (inverse) | 1 parcours, n paliers |
| Scénario ↔ Parcours | pivot `scenario_parcours` | **1-1** (unique des deux côtés) |
| Professeur ↔ Parcours | pivot `professeur_parcours` | n-n |
| Palier → DossierTechnique | one_to_one | 1 palier, 1 dossier |
| DossierTechnique → RessourceDossier | many_to_one (inverse) | 1 dossier, n ressources |
| DossierTechnique → QCM | one_to_one | 1 dossier, 1 QCM |
| Élève → ProgressionParcours → Parcours | associative | n-n via ProgressionParcours |
| ProgressionParcours → ProgressionPalier | many_to_one (inverse) | 1 progression, n paliers suivis |

## Règles métier & cycle de vie

- **Réutilisation** : un parcours rattaché à un `NiveauClasse` stable se réemploie d'année
  en année (l'année vit sur la `Classe`, pas sur le parcours).
- **Ordre des paliers** unique et contigu (1..n) dans le parcours.
- **Publication** : portée par `parcours.statut` (plus de table de versions).
- **Parcours du dossier** : lecture du **DossierTechnique** → réussite du **QCM** → accès
  à l'**Activité** (règle de progression, ADR-021 côté écran).
- **Pas de gel de version** : modifier un parcours affecte les progressions en cours
  (assumé en mono-établissement, ADR-022).

## Portée

Couvre `Parcours`, `Palier`, `DossierTechnique`, `RessourceDossier`, `QCM`,
`ProgressionParcours`. En amont : le [**Scénario**](dictionnaire-scenario.md) (apparié 1-1).
En aval : l'**exécution élève** et le [**Bilan**](dictionnaire-bilan.md) (Bloc B).
