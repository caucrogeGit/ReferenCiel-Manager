# Contrat du JSON canonique — Starter Welcome

Spécifie la **forme** du JSON canonique de type **`starter_welcome`** : un parcours
pédagogique réutilisable (paliers → dossier technique / QCM / activité / checklist).
Modelé sur le starter numérisé `sources/starters/welcome-reseau/`.

> Partage l'**enveloppe commune** du [contrat référentiel](contrat-referentiel-niveau-classe.md)
> (§2-§3). Ce document ne couvre que le **corps `starter_welcome`**. Ni schéma de
> validation ni JSON réel complet (tickets suivants).

## 1. Principe

Un starter est **riche en contenu** (dossiers techniques, images ~30 Mo). Son JSON
canonique est donc un **manifeste** qui **référence** ses contenus par chemin
relatif, pas un fichier auto-contenu :

```text
référentiel niveau-classe : JSON auto-contenu (données)
starter_welcome           : JSON manifeste + bundle (contenus md + images)
```

**Upload (ADR-008)** : un starter s'importe sous forme de **bundle** (archive)
contenant le manifeste JSON et les fichiers référencés. L'application valide le
manifeste (schéma) puis importe paliers/QCM/checklists en base et stocke les
contenus/fichiers (opt-in `files`).

## 2. Enveloppe commune

Identique au contrat référentiel : `type` (= `starter_welcome`), `identifiant`
(ex. `welcome-reseau`), `version`, `sources[]`, `provenance{}`. Chaque élément
repris porte `source_ids`.

## 3. Cadre du starter

| Champ | Type | Obligatoire | Rôle |
|---|---|:--:|---|
| `niveau_classe` | object `{code, intitule}` | oui | classe visée (ex. `2TNE`) |
| `titre` | string | oui | ex. « Semaine réseau et virtualisation » |
| `presentation` | string \| ref | non | texte d'accueil (par ref de fichier possible) |
| `organisation` | object | oui | `{ activite_glissante: bool, ordre_impose: bool }` |
| `paliers` | array | oui | voir §4 |

## 4. Palier

| Champ | Type | Obligatoire | Rôle |
|---|---|:--:|---|
| `id` | string | oui | ex. `palier-1` |
| `ordre` | integer | oui | rang (1..n), unique |
| `titre` | string | oui | ex. « Fabriquer et tester un câble T568B » |
| `theme` | string | non | ex. « Câble Ethernet droit » |
| `production_attendue` | string | non | ex. « Un câble droit conforme » |
| `dossier_technique` | ref | oui | `{ fichier: "palier-1/dossier-technique.md" }` |
| `qcm` | object | non | voir §5 |
| `activite` | object | non | `{ id, objectif?, fichier? , etapes?[] }` |
| `checklist` | object | non | voir §6 |
| `images` | array | non | `[{ fichier, legende }]` |
| `ressources` | object | non | `{ eleve: [ref], professeur: [ref] }` |

## 5. QCM

| Champ | Type | Obligatoire | Rôle |
|---|---|:--:|---|
| `id` | string | oui | ex. `qcm-palier-1` |
| `format_reponse` | string | non | ex. « une réponse par ligne, `1a` » |
| `validation` | object | oui | `{ seuil: "100%" }` |
| `questions` | array | oui | voir ci-dessous |

`questions[]` : `{ numero: int, enonce: string, choix: [{ lettre: "A"\|"B"\|"C", texte: string }], bonne_reponse: "A"\|"B"\|"C" }`.

> La `bonne_reponse` provient du **corrigé** : la canonicalisation **fusionne** le
> QCM élève (énoncés + choix) et le corrigé (bonnes réponses + explications). Le
> canonique est donc plus riche que chaque source prise isolément.

## 6. Checklist

| Champ | Type | Obligatoire | Rôle |
|---|---|:--:|---|
| `id` | string | oui | ex. `checklist-palier-1` |
| `sections` | array | oui | `[{ numero, titre, items: [{ libelle }] }]` |
| `decision_finale` | array | non | `[{ etat, decision }]` (validé / à reprendre / correction ciblée) |

> Les colonnes de validation **élève/professeur** sont un état d'exécution
> (`Progression` / `ÉvaluationCritère`), pas une donnée de définition : le canonique
> porte les **items à vérifier**, pas leurs cases cochées.

## 7. Lien optionnel au référentiel

Un starter peut **aligner** ses paliers sur les compétences d'un référentiel
niveau-classe :

```text
relations.palier_competences[] : { palier: <id>, competences: [<C0x>...] }
```

**Optionnel et relevant du jugement pédagogique** (domaine du professeur) : non
imposé, à renseigner par le professeur. Le contenu du starter ne fournit pas ce
mapping mécaniquement.

## 8. Invariants

- `ordre` des paliers **unique et contigu** (1..n).
- Toute `bonne_reponse` d'une question ∈ les `lettre` de ses `choix`.
- Tout `fichier`/`ref` pointe vers un contenu **présent dans le bundle**.
- Provenance obligatoire (`source_ids`) sur les éléments repris.
- Vocabulaire : pôles ≠ rôles ; définition (contenus) ≠ exécution (progression).

## 9. Fragment d'illustration (vérifiable)

Extrait du palier 1 (câble T568B). **Illustration, pas un manifeste complet.**

```json
{
  "type": "starter_welcome",
  "identifiant": "welcome-reseau",
  "version": "0.1.0",
  "sources": [
    { "source_id": "starter-welcome-reseau", "source_type": "starter", "source_fichier": "sources/starters/welcome-reseau/" }
  ],
  "provenance": { "date_extraction": "2026-07-06", "methode": "numerisation manuelle", "point_entree": "referentiel_officiel" },
  "niveau_classe": { "code": "2TNE", "intitule": "Seconde TNE CIEL" },
  "titre": "Semaine réseau et virtualisation",
  "organisation": { "activite_glissante": true, "ordre_impose": true },
  "paliers": [
    {
      "id": "palier-1", "ordre": 1, "titre": "Fabriquer et tester un câble Ethernet droit T568B",
      "theme": "Câble Ethernet droit", "production_attendue": "Un câble droit conforme",
      "dossier_technique": { "fichier": "palier-1/dossier-technique.md" },
      "qcm": {
        "id": "qcm-palier-1", "validation": { "seuil": "100%" },
        "questions": [
          { "numero": 6, "enonce": "Un câble Ethernet contient généralement combien de fils ?",
            "choix": [ { "lettre": "A", "texte": "2" }, { "lettre": "B", "texte": "4" }, { "lettre": "C", "texte": "8" } ],
            "bonne_reponse": "C" }
        ]
      },
      "activite": { "id": "activite-palier-1", "fichier": "palier-1/eleve/activite-palier-1.md" },
      "checklist": {
        "id": "checklist-palier-1",
        "sections": [ { "numero": 7, "titre": "Étape 5 — test au testeur RJ45", "items": [ { "libelle": "Le résultat est comparé au résultat attendu (1→1 … 8→8)" } ] } ]
      },
      "images": [ { "fichier": "palier-1/images/norme-t568b.png", "legende": "Norme T568B" } ],
      "source_ids": ["starter-welcome-reseau"]
    }
  ]
}
```

## 10. Schéma de validation

Outillé par [`schemas/schema-json-canonique-starter-welcome.json`](schemas/schema-json-canonique-starter-welcome.json)
(JSON Schema 2020-12) — porte de validation des uploads (ADR-008). Le schéma valide
la structure ; les invariants sémantiques (ordre unique/contigu, `bonne_reponse` ∈
`choix`, fichiers présents dans le bundle) sont validés par l'importeur.

## 11. Hors de ce contrat

- Le **manifeste canonique complet** du Welcome Réseau (canonicalisation, ticket
  suivant).
- Le dictionnaire de données, les entités Forge, le SQL, l'import (tickets de
  programmation, à faire ensemble).
