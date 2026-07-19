# Dictionnaire de données : Séquence

Documentation **métier enrichie** du domaine « séquence » : ce qui **organise le travail
élève** (instructions §12). Objets **persistés en base** (ADR-003).

> **Modèle canonique aplati (ADR-022).** La **Séquence** est l'objet racine, rattaché
> directement à un **NiveauClasse**. Elle se découpe en **Séances** ; chaque séance porte
> un **DossierTechnique** (ressources + QCM de validation). Un **Scénario** lui est
> apparié (1-1). L'élève progresse via une **ProgressionSequence**, ancrée à une
> **affectation** qui **fige un instantané** de la séquence (ADR-026).

## Principes

- **Nommage / types / relations** : conventions Forge (comme les autres dictionnaires).
- **Base = vérité** (ADR-003). La séquence est **créé par le professeur** (`Professeur n-n
  Séquence`) pour un **NiveauClasse** stable, donc **réutilisable d'une année sur l'autre**.
- **Pas de couche gabarit/versions** : les entités `StarterWelcome`, `VersionStarter`,
  `VersionParcours` et `AffectationParcours` ont été **supprimées** (ADR-022). La publication
  se lit sur le champ `statut` de la séquence ; le suivi élève est porté par
  `ProgressionSequence`. **L'affectation est réintroduite par l'ADR-026**
  comme déclencheur du **gel par instantané** : une séquence figée ne change plus
  sous les pieds de l'élève.

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
| `prerequis` | text | non | prérequis attendus (peut être explicitement vide) |
| `positionnement_progression` | text | non | place dans la progression annuelle |
| `duree_estimee` | string | non | durée globale estimée (indicative) |
| `modalites_evaluation` | text | non | modalités générales d'évaluation |

> **Frontière Scénario ↔ Séquence (SEQ-02, décision A).** Le « cadre » pédagogique
> — contexte professionnel, problématique, objectifs, **compétences** et **critères** —
> vit sur le **Scénario** (déjà en base, édité par le tunnel), lu en **1-1**. La séquence
> n'ajoute que l'incrémental ci-dessus, pour ne rien dupliquer.

### Séance

Le **découpage de la séquence** en étapes. Rattaché **directement** à la séquence.

| Champ | Type | Oblig. | Description / règle |
|---|---|:--:|---|
| `sequence_id` | many_to_one → Séquence | oui | séquence parent |
| `ordre` | integer | oui | rang 1..n, **unique** dans la séquence `(sequence_id, ordre)` |
| `titre` | string | oui | |
| `theme` | string | non | |
| `production_attendue` | string | non | ex. « Un câble droit conforme » |
| `objectif_operationnel` | text | non | ce que l'élève saura faire au terme de la séance |
| `consigne_generale` | text | non | consigne / description générale du travail |
| `duree_estimee_minutes` | integer | non | durée estimée (indicative, pas un créneau strict) |
| `modalite_pedagogique` | string | non | ex. individuel, binôme, groupe |
| `condition_realisation` | text | non | ce qui permet de considérer la séance faite |
| `condition_validation` | text | non | ce qui permet de la valider (règle de passage) |
| `remediation` | text | non | remédiation éventuelle |

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
| Séquence ↔ SavoirAssocié | pivot `sequence_savoir_associe` | n-n |
| Séance ↔ Competence | pivot `seance_competence` (rôle : travaillée/observée/évaluée) | n-n |
| Séance ↔ CritereObservable | pivot `seance_critere` | n-n |
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
- **Gel par instantané (ADR-026)** : une séquence est **figée à l'affectation** ;
  modifier le maître n'affecte **pas** les progressions déjà figées.

### Cycle de vie de la paire Scénario ↔ Séquence

- **Appairage 1-1 obligatoire.** L'objet de conception réel est la **paire** : à toute
  séquence correspond exactement un scénario et réciproquement, **inséparables**. Un
  scénario n'est **pas** un objet réutilisable qui vivrait seul durablement ni partagé
  entre séquences.
- **Titre : autorité au Scénario.** Le titre est porté par le **scénario** ; la séquence
  l'affiche depuis lui (les deux portent donc toujours le même titre, sans double source
  de vérité).
- **Création (deux entrées, même résultat : une paire).**
  - *Séquence d'abord* : on remplit la séquence (y compris les champs « cadre ») et le
    **scénario est créé en même temps** avec ces valeurs.
  - *Scénario d'abord* (tunnel actuel) : on crée le scénario, puis on **lie** une séquence ;
    le « cadre » de la séquence est alors **lu depuis le scénario**.
  - Dans les deux cas, on aboutit à une paire appairée ; aucun des deux ne reste seul.
- **Finalisation à trois niveaux** (complétude **dérivée**, cohérente ADR-026 — « finalisé »
  n'est pas un statut persisté) :
  - **Scénario finalisé** = tout son tunnel obligatoire est saisi ;
  - **Séquence finalisée** = tout son tunnel obligatoire est saisi ;
  - **Ensemble finalisé** = les deux finalisés.
  - La **publication** (`statut = publié`) s'applique à l'**ensemble** et n'est possible que
    si l'ensemble est finalisé.

## Portée

Couvre `Séquence`, `Séance`, `DossierTechnique`, `RessourceDossier`, `QCM`,
`ProgressionSequence`. En amont : le [**Scénario**](dictionnaire-scenario.md) (apparié 1-1).
En aval : l'**exécution élève** et le [**Bilan**](dictionnaire-bilan.md) (Bloc B).
