# Contrat du JSON canonique : enveloppe commune + référentiel niveau-classe

Ce document **spécifie la forme** attendue des JSON canoniques (pas leur contenu).
Il définit une **enveloppe commune** à tous les JSON canoniques, puis le **corps du
type « référentiel niveau-classe »** en deux couches (famille TNE + cible CIEL).

> Ce n'est **pas** un JSON réel (ticket 03), **ni** un schéma de validation
> (ticket 04).
> Le type « Starter Welcome » aura son propre contrat.
> Fondé sur la
> capitalisation `.scpro` (§7 squelette, §8 provenance), la trace CIEL 2TNE
> (deux couches) et les sources enregistrées.

## 1. Principe

Tout JSON canonique partage une **enveloppe commune** et porte un **corps typé**,
discriminé par le champ `type` :

```text
enveloppe commune  +  corps( type )
```

`type` connus : `referentiel_niveau_classe` (spécifié ici), `starter_welcome`
(contrat à venir).

## 2. Enveloppe commune

| Champ | Type | Obligatoire | Rôle |
|---|---|:--:|---|
| `type` | string (enum) | oui | discriminant du corps |
| `identifiant` | string (kebab-case) | oui | id stable du document (ex. `ciel-2tne`) |
| `version` | string (semver) | oui | version du document canonique (ex. `0.1.0`) |
| `sources` | array | oui | descripteurs des sources (voir §3) |
| `provenance` | object | oui | contexte d'extraction (date, méthode, point d'entrée) |

`provenance{}` : `{ "date_extraction": "AAAA-MM-JJ", "methode": "extraction manuelle | assistée", "point_entree": "referentiel_officiel | cpro_scpro" }`.

## 3. Modèle de provenance (sources)

Chaque entrée de `sources[]` décrit une source (modèle §8 de la capitalisation) :

| Champ | Type | Obligatoire | Exemple |
|---|---|:--:|---|
| `source_id` | string | oui | `referentiel-bac-pro-ciel` |
| `source_type` | string (enum) | oui | `pdf_officiel` \| `scpro` \| `odt` \| `starter` |
| `source_fichier` | string | oui | `referenciel-bac-pro-ciel.pdf` |
| `source_note` | string | non | « Référentiel officiel utilisé pour validation » |

**Règle** : tout élément repris, extrait, reconstruit ou adapté porte une trace de
provenance via `source_ids: [ ... ]` (références à `sources[].source_id`).

## 4. Corps « référentiel niveau-classe »

### 4.1 Cadre

| Champ | Type | Obligatoire | Rôle |
|---|---|:--:|---|
| `formation` | object | oui | `{ code, intitule }` (ex. Bac Pro CIEL) |
| `niveau_classe` | object | oui | `{ code, intitule }` (ex. `2TNE`) |

### 4.2 Couche cible CIEL

| Collection | Élément (champs principaux) |
|---|---|
| `poles_activites[]` | `id`, `intitule`, `source_ids` |
| `activites_professionnelles[]` | `id`, `code` (E1, R2, D3…), `intitule`, `pole_id`, `taches[]`, `conditions_exercice{ moyens[], autonomie, }`, `resultats_attendus[]` (`{ id, libelle }`), `source_ids` |
| `competences[]` | `id`, `code` (C01…C11), `intitule`, `connaissances[]` (`{ libelle, niveau_taxonomique }`), `criteres_evaluation[]` (`{ id, libelle }`), `source_ids` |
| `indicateurs_reussite[]` | `id`, `libelle`, `origine` (`resultat_attendu` \| `critere` \| `reformulation`), `ref` (id d'origine), `source_ids` |

### 4.3 Relations

```text
relations {
  activites_competences[]      : { activite: <code>, competences: [<code>...] }
  competences_criteres[]       : { competence: <code>, criteres: [<id>...] }
  activites_resultats_attendus[]: { activite: <code>, resultats: [<id>...] }
}
```

## 5. Couche famille TNE (2ⁿᵈᵉ)

La 2ⁿᵈᵉ travaille les **compétences communes de la famille TNE** (`CC1…CC9`), qu'on
mappe vers la cible CIEL.

| Collection | Élément |
|---|---|
| `famille_competences[]` | `code` (CC1…CC9), `intitule`, `source_ids` |
| `relations.cc_competences[]` | `{ cc: <CCx>, competences: [<C0x>...] }`, mapping famille ↔ CIEL |

## 6. Invariants

- Tout `id` / `code` est **unique** dans sa collection.
- Toute relation ne référence que des `id`/`code` **existants** (références résolues).
- Tout élément extrait porte **`source_ids` non vide** (provenance obligatoire).
- Les trois notions restent **distinctes** :

```text
resultats_attendus   = liés aux activités professionnelles
criteres_evaluation  = liés aux compétences
indicateurs_reussite = formulation pédagogique exploitable (dérivée)
```

- On parle de **pôles d'activités**, jamais de « rôles » (réservés à `eleve`,
  `professeur`, `administrateur`).

## 7. Fragment d'illustration (vérifiable)

Extrait minimal illustrant la forme (trace de travail : pôle « Réalisation et
maintenance de produits électroniques », activité **E1**, compétences
**C03, C04, C07**).
**Illustration, pas un JSON canonique complet** (ticket 03).

```json
{
  "type": "referentiel_niveau_classe",
  "identifiant": "ciel-2tne",
  "version": "0.1.0",
  "sources": [
    { "source_id": "referentiel-bac-pro-ciel", "source_type": "pdf_officiel", "source_fichier": "referenciel-bac-pro-ciel.pdf" },
    { "source_id": "vademecum-tne-2nde", "source_type": "pdf_officiel", "source_fichier": "referenciel-2tne.pdf" }
  ],
  "provenance": { "date_extraction": "2026-07-05", "methode": "extraction manuelle", "point_entree": "referentiel_officiel" },
  "formation": { "code": "BACPRO-CIEL", "intitule": "Bac Pro Cybersécurité, Informatique et réseaux, Électronique" },
  "niveau_classe": { "code": "2TNE", "intitule": "Seconde famille des métiers des transitions numérique et énergétique" },
  "poles_activites": [
    { "id": "pole-real-maint-elec", "intitule": "Réalisation et maintenance de produits électroniques", "source_ids": ["referentiel-bac-pro-ciel"] }
  ],
  "activites_professionnelles": [
    { "id": "act-e1", "code": "E1", "intitule": "Étude et conception de produits électroniques", "pole_id": "pole-real-maint-elec",
      "taches": ["Analyse et saisie d'un schéma", "Placement et routage", "Réalisation d'un prototype"],
      "resultats_attendus": [ { "id": "ra-e1-1", "libelle": "Le prototype réalisé est conforme au cahier des charges" } ],
      "source_ids": ["referentiel-bac-pro-ciel"] }
  ],
  "competences": [
    { "id": "comp-c03", "code": "C03", "intitule": "Participer à un projet",
      "criteres_evaluation": [ { "id": "cr-c03-1", "libelle": "Le suivi du projet est respecté" } ], "source_ids": ["referentiel-bac-pro-ciel"] },
    { "id": "comp-c04", "code": "C04", "intitule": "Analyser une structure matérielle et logicielle", "source_ids": ["referentiel-bac-pro-ciel"] },
    { "id": "comp-c07", "code": "C07", "intitule": "Réaliser des maquettes et prototypes", "source_ids": ["referentiel-bac-pro-ciel"] }
  ],
  "famille_competences": [
    { "code": "CC3", "intitule": "Analyser et exploiter les données", "source_ids": ["vademecum-tne-2nde"] }
  ],
  "relations": {
    "activites_competences": [ { "activite": "E1", "competences": ["C03", "C04", "C07"] } ],
    "competences_criteres": [ { "competence": "C03", "criteres": ["cr-c03-1"] } ],
    "activites_resultats_attendus": [ { "activite": "E1", "resultats": ["ra-e1-1"] } ],
    "cc_competences": [ { "cc": "CC3", "competences": ["C04"] } ]
  }
}
```

## 8. Hors de ce contrat

- Le **JSON canonique réel complet** CIEL 2TNE (ticket 03).
- Le **schéma JSON** de validation (ticket 04).
- Le contrat du type **`starter_welcome`** (ticket dédié) ; seule l'enveloppe
  commune (§2-§3) est posée pour l'accueillir.
- Le dictionnaire de données, les entités Forge, le SQL (tickets ultérieurs).

## 9. Schéma de validation (ticket 04)

Ce contrat est outillé par un schéma JSON (JSON Schema 2020-12) :
[`schemas/schema-json-canonique-referentiel-niveau-classe.json`](schemas/schema-json-canonique-referentiel-niveau-classe.json).

C'est la **porte de validation des uploads** (ADR-009).
Répartition :

- **Validé par le schéma** : présence des familles obligatoires, types, énumérations
  (`type`, `source_type`, `point_entree`, `origine`), motifs des codes
  (`E1`/`R2`/`D3`, `C0x`, `CCx`), semver, niveaux taxonomiques 1–4. Les champs
  additionnels sont tolérés (« peut être plus riche »).
- **Validé par l'importeur** (hors schéma) : **unicité** des `id`/`code` dans chaque
  collection et **résolution** des références de `relations` vers des éléments
  existants, invariants sémantiques non exprimables en JSON Schema pur.
