# Contrat du JSON canonique : Séquence

Spécifie la **forme** du JSON canonique de type **`sequence`** : une séquence
pédagogique canonique (rattachée à un niveau-classe ; séances → dossier technique /
QCM / activité / checklist). Modelé sur le starter numérisé
`sources/starters/welcome-reseau/` (matière première canonicalisée en séquence).

> **Modèle canonique (ADR-022).** La **Séquence** est l'objet racine du domaine
> pédagogique. La couche gabarit/versions (`StarterWelcome`, `VersionStarter`,
> `VersionParcours`) a été supprimée : le manifeste décrit **directement** une séquence.
> Voir [ADR-022](../../adr/022-parcours-objet-canonique-aplatissement.md) et le
> [dictionnaire Séquence](../data-dictionary/dictionnaire-sequence.md).

> Partage l'**enveloppe commune** du [contrat référentiel](contrat-referentiel-niveau-classe.md)
> (§2-§3). Ce document ne couvre que le **corps `sequence`**.

## 1. Principe

Une séquence est **riche en contenu** (dossiers techniques, images ~30 Mo). Son JSON
canonique est donc un **manifeste** qui **référence** ses contenus par chemin
relatif, pas un fichier auto-contenu :

```text
référentiel niveau-classe : JSON auto-contenu (données)
séquence                  : JSON manifeste + bundle (contenus md + images)
```

**Upload (ADR-009)** : une séquence s'importe sous forme de **bundle** (archive)
contenant le manifeste JSON et les fichiers référencés. L'application valide le
manifeste (schéma) puis importe séances/dossiers/QCM/checklists en base et stocke
les contenus/fichiers (opt-ins `files`, `video`, `audio`).

## 2. Enveloppe commune

Identique au contrat référentiel : `type` (= `sequence`), `identifiant`
(ex. `welcome-reseau`), `version`, `sources[]`, `provenance{}`. Chaque élément
repris porte `source_ids`.

## 3. Cadre de la séquence

| Champ | Type | Obligatoire | Rôle |
|---|---|:--:|---|
| `niveau_classe` | object `{code, intitule}` | oui | niveau visé (ex. `2TNE`), stable inter-années |
| `titre` | string | oui | ex. « Semaine réseau et virtualisation » |
| `presentation` | string \| ref | non | texte d'accueil (par ref de fichier possible) |
| `statut` | string | non | `brouillon` \| `finalise` \| `publie` \| `attribue` (défaut `brouillon`, ADR-034) |
| `organisation` | object | oui | `{ activite_glissante: bool, ordre_impose: bool }` |
| `seances` | array | oui | voir §4 |

## 4. Séance

| Champ | Type | Obligatoire | Rôle |
|---|---|:--:|---|
| `id` | string | oui | ex. `seance-1` |
| `ordre` | integer | oui | rang (1..n), unique |
| `titre` | string | oui | ex. « Fabriquer et tester un câble T568B » |
| `theme` | string | non | ex. « Câble Ethernet droit » |
| `production_attendue` | string | non | ex. « Un câble droit conforme » |
| `dossier_technique` | object | oui | conteneur de ressources, voir §4bis |
| `qcm` | object | non | voir §5 |
| `activite` | object | non | `{ id, objectif?, fichier?, etapes?[] }` |
| `checklist` | object | non | voir §6 |
| `ressources` | object | non | `{ eleve: [ref], professeur: [ref] }` |

## 4bis. Dossier technique (conteneur de ressources)

Le dossier technique n'est plus un fichier unique : c'est un **conteneur** de
ressources typées (entité `DossierTechnique` → `RessourceDossier`).

| Champ | Type | Obligatoire | Rôle |
|---|---|:--:|---|
| `titre` | string | non | titre du dossier |
| `ressources` | array | oui | `[{ type, titre, ordre, … }]` |

`ressources[]` — le champ de contenu dépend du `type` :

| `type` | contenu |
|---|---|
| `markdown` | `contenu` (inline) ou `fichier` (ref bundle) |
| `video` | `fichier` (ingéré → opt-in `video`) ou `url` (source) |
| `audio` | `fichier` (ingéré → opt-in `audio`) ou `url` (source) |
| `lien` | `url` (lien externe, non téléchargé) |

## 5. QCM

Le QCM de **validation** du dossier technique (à réussir avant l'activité).

| Champ | Type | Obligatoire | Rôle |
|---|---|:--:|---|
| `id` | string | oui | ex. `qcm-seance-1` |
| `format_reponse` | string | non | ex. « une réponse par ligne, `1a` » |
| `validation` | object | oui | `{ seuil: "100%" }` |
| `questions` | array | oui | voir ci-dessous |

`questions[]` : `{ numero: int, enonce: string, choix: [{ lettre: "A"\|"B"\|"C", texte: string }], bonne_reponse: "A"\|"B"\|"C" }`.

> La `bonne_reponse` provient du **corrigé** : la canonicalisation **fusionne** le
> QCM élève (énoncés + choix) et le corrigé (bonnes réponses + explications).

## 6. Checklist

| Champ | Type | Obligatoire | Rôle |
|---|---|:--:|---|
| `id` | string | oui | ex. `checklist-seance-1` |
| `sections` | array | oui | `[{ numero, titre, items: [{ libelle }] }]` |
| `decision_finale` | array | non | `[{ etat, decision }]` (validé / à reprendre / correction ciblée) |

> Les colonnes de validation **élève/professeur** sont un état d'exécution
> (`ProgressionSequence` / `ProgressionSeance`), pas une donnée de définition : le
> canonique porte les **items à vérifier**, pas leurs cases cochées.

## 7. Lien optionnel au référentiel

Une séquence peut **aligner** ses séances sur les compétences d'un référentiel
niveau-classe :

```text
relations.seance_competences[] : { seance: <id>, competences: [<C0x>...] }
```

**Optionnel et relevant du jugement pédagogique** (domaine du professeur) : non
imposé. Le contenu de la séquence ne fournit pas ce mapping mécaniquement.

## 8. Invariants

- `ordre` des séances **unique et contigu** (1..n).
- Toute `bonne_reponse` d'une question ∈ les `lettre` de ses `choix`.
- Tout `fichier`/`ref` pointe vers un contenu **présent dans le bundle**.
- Provenance obligatoire (`source_ids`) sur les éléments repris.
- Vocabulaire : pôles ≠ rôles ; définition (contenus) ≠ exécution (progression).

## 9. Fragment d'illustration (vérifiable)

Extrait de la séance 1 (câble T568B). **Illustration, pas un manifeste complet.**

```json
{
  "type": "séquence",
  "identifiant": "welcome-reseau",
  "version": "0.1.0",
  "sources": [
    { "source_id": "starter-welcome-reseau", "source_type": "starter", "source_fichier": "sources/starters/welcome-reseau/" }
  ],
  "provenance": { "date_extraction": "2026-07-06", "methode": "numerisation manuelle", "point_entree": "referentiel_officiel" },
  "niveau_classe": { "code": "2TNE", "intitule": "Seconde TNE CIEL" },
  "titre": "Semaine réseau et virtualisation",
  "statut": "publie",
  "organisation": { "activite_glissante": true, "ordre_impose": true },
  "séances": [
    {
      "id": "seance-1", "ordre": 1, "titre": "Fabriquer et tester un câble Ethernet droit T568B",
      "theme": "Câble Ethernet droit", "production_attendue": "Un câble droit conforme",
      "dossier_technique": {
        "titre": "Dossier technique — Câblage",
        "ressources": [
          { "type": "markdown", "titre": "Consignes", "ordre": 1, "fichier": "seance-1/dossier-technique.md" },
          { "type": "lien", "titre": "Norme T568B", "ordre": 2, "url": "https://example.org/t568b" }
        ]
      },
      "qcm": {
        "id": "qcm-seance-1", "validation": { "seuil": "100%" },
        "questions": [
          { "numero": 6, "enonce": "Un câble Ethernet contient généralement combien de fils ?",
            "choix": [ { "lettre": "A", "texte": "2" }, { "lettre": "B", "texte": "4" }, { "lettre": "C", "texte": "8" } ],
            "bonne_reponse": "C" }
        ]
      },
      "activite": { "id": "activite-seance-1", "fichier": "seance-1/eleve/activite-seance-1.md" },
      "checklist": {
        "id": "checklist-seance-1",
        "sections": [ { "numero": 7, "titre": "Étape 5 — test au testeur RJ45", "items": [ { "libelle": "Le résultat est comparé au résultat attendu (1→1 … 8→8)" } ] } ]
      },
      "source_ids": ["starter-welcome-reseau"]
    }
  ]
}
```

## 10. Schéma de validation

Outillé par [`schemas/schema-json-canonique-sequence.json`](schemas/schema-json-canonique-sequence.json)
(JSON Schema 2020-12) : porte de validation des uploads (ADR-009). Le schéma valide
la structure ; les invariants sémantiques (ordre unique/contigu, `bonne_reponse` ∈
`choix`, fichiers présents dans le bundle) sont validés par l'importeur.

## 11. Hors de ce contrat

- Le **manifeste canonique complet** du Welcome Réseau (canonicalisation, ticket
  suivant).
- Le SQL, l'import et les écrans (tickets de programmation).
